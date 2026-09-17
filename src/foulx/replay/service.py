"""
Replay Service API for FOUL-X M9.0 Replay Engine.

High-level interface managing replay clock, resolver, snapshot builder, and manifest.
"""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import pandas as pd

from src.physics.state_estimator import PhysicsStateEstimator
from src.models.features import extract_causal_features_for_exchanger
from src.models.schemas import FeatureConfig
from src.models.ridge_forecaster import RidgeFoulingForecaster
from src.foulx.gate.checks import HistoricalRegimeSupportChecker
from src.foulx.replay.clock import ReplayClock
from src.foulx.replay.resolver import HistoricalStateResolver, VALID_EXCHANGERS
from src.foulx.replay.schemas import ReplaySnapshot, ReplayMode, ReplayManifest
from src.foulx.replay.snapshot import ReplaySnapshotBuilder
from src.foulx.replay.reason_codes import ReplayReasonCode


class ReplayService:
    """
    FOUL-X M9.0 Deterministic Replay Service.
    Manages deterministic replay snapshots, historical resolver, replay clock, and model state.
    """

    def __init__(self, data_path: Path = Path("data/raw/heat_exchanger_fouling_dataset.csv")):
        self.resolver = HistoricalStateResolver(data_path=data_path)
        t_min, t_max = self.resolver.get_min_max_timestamps()
        self.clock = ReplayClock(min_timestamp=t_min, max_timestamp=t_max, step_hours=1.0)

        # Initialize M2 Physics State Estimator
        df_all = self.resolver._get_df()
        self.physics_engine = PhysicsStateEstimator()
        self.physics_engine.fit_baseline_from_dataframe(df_all, clean_window_hours=100.0)

        # Initialize M4 Forecaster & M5 Regime Checker fitted ONCE strictly on Train split (t <= 44,799)
        train_mask = df_all["Time_hr"] <= 44799
        feat_config = FeatureConfig(window_sizes=[6, 24, 72, 168], target_horizon=24)
        X_all, y_target_all = extract_causal_features_for_exchanger(df_all, "E01", self.physics_engine, feat_config)

        feature_cols = [c for c in X_all.columns if c != "R_f_derived" and not c.startswith("Time_hr")]
        X_train = X_all.loc[train_mask, feature_cols].fillna(0.0)
        y_train = y_target_all.shift(-24).loc[train_mask].fillna(0.0)

        self.forecaster = RidgeFoulingForecaster(alpha=1.0)
        self.forecaster.fit(X_train, y_train)

        self.regime_checker = HistoricalRegimeSupportChecker(z_score_threshold=4.0)
        self.regime_checker.fit_on_training_data(X_train)

        self.snapshot_builder = ReplaySnapshotBuilder(
            physics_engine=self.physics_engine,
            forecaster=self.forecaster,
            regime_checker=self.regime_checker,
        )

        self.current_exchanger_id = "E01"
        self.current_scenario_mode = ReplayMode.NORMAL

    def get_manifest(self) -> ReplayManifest:
        """Returns replay manifest metadata."""
        t_min, t_max = self.resolver.get_min_max_timestamps()
        return ReplayManifest(
            min_timestamp=t_min,
            max_timestamp=t_max,
            step_size_hours=self.clock.step_hours,
        )

    def get_snapshot(
        self,
        timestamp: float,
        exchanger_id: str = "E01",
        scenario_mode: ReplayMode = ReplayMode.NORMAL,
    ) -> ReplaySnapshot:
        """
        Constructs deterministic ReplaySnapshot for given timestamp, exchanger_id, and scenario_mode.
        Strictly guarantees ZERO future data leakage.
        """
        if exchanger_id not in VALID_EXCHANGERS:
            raise ValueError(f"Unknown exchanger_id '{exchanger_id}'. Supported: {list(VALID_EXCHANGERS.keys())}")

        raw_record, _ = self.resolver.resolve_raw_record(timestamp)
        causal_history_df = self.resolver.resolve_causal_history(timestamp, window_hours=168)

        return self.snapshot_builder.build_snapshot(
            timestamp=timestamp,
            exchanger_id=exchanger_id,
            scenario_mode=scenario_mode,
            raw_record=raw_record,
            causal_history_df=causal_history_df,
        )

    def get_current_snapshot(self) -> ReplaySnapshot:
        """Gets snapshot at current clock timestamp."""
        return self.get_snapshot(
            timestamp=self.clock.current_timestamp,
            exchanger_id=self.current_exchanger_id,
            scenario_mode=self.current_scenario_mode,
        )

    def seek(self, timestamp: float) -> ReplaySnapshot:
        """Seeks clock to timestamp and returns snapshot."""
        t_new = self.clock.seek(timestamp)
        return self.get_snapshot(t_new, self.current_exchanger_id, self.current_scenario_mode)

    def step_forward(self) -> ReplaySnapshot:
        """Steps clock forward and returns snapshot."""
        t_new = self.clock.step_forward()
        return self.get_snapshot(t_new, self.current_exchanger_id, self.current_scenario_mode)

    def step_backward(self) -> ReplaySnapshot:
        """Steps clock backward and returns snapshot."""
        t_new = self.clock.step_backward()
        return self.get_snapshot(t_new, self.current_exchanger_id, self.current_scenario_mode)

    def reset(self, start_timestamp: Optional[float] = None) -> ReplaySnapshot:
        """Resets clock and returns snapshot."""
        t_new = self.clock.reset(start_timestamp)
        return self.get_snapshot(t_new, self.current_exchanger_id, self.current_scenario_mode)
