"""
Canonical Snapshot Builder for FOUL-X M9.0 Replay Engine.

Executes M2-M6 pipeline on resolved historical state at t and constructs ReplaySnapshot.
"""

from typing import Dict, Any, List, Optional
import pandas as pd

from src.physics.state_estimator import PhysicsStateEstimator, EXCHANGER_MAPPING
from src.models.features import extract_causal_features_for_exchanger
from src.models.schemas import FeatureConfig
from src.models.ridge_forecaster import RidgeFoulingForecaster
from src.foulx.gate.checks import HistoricalRegimeSupportChecker
from src.foulx.gate.evaluator import ReliabilityGateEvaluator
from src.foulx.decision.evaluator import DecisionEngineEvaluator
from src.foulx.decision.thresholds import DecisionThresholdConfig, DEFAULT_DECISION_THRESHOLDS
from src.forecast.schemas import ForecastResult, ForecastStatus
from src.foulx.evaluation.policies import FixedPolicy
from src.foulx.evaluation.perturbations import SyntheticRegimeShiftPerturber
from src.foulx.replay.schemas import (
    ReplaySnapshot,
    ReplayMode,
    ReplayProvenance,
)
from src.foulx.replay.reason_codes import ReplayReasonCode


class ReplaySnapshotBuilder:
    """
    Constructs a canonical ReplaySnapshot for timestamp t, exchanger_id, and scenario_mode.
    Uses existing validated M2, M4, M5, and M6 engineering logic.
    """

    def __init__(
        self,
        physics_engine: PhysicsStateEstimator,
        forecaster: Optional[RidgeFoulingForecaster] = None,
        regime_checker: Optional[HistoricalRegimeSupportChecker] = None,
        perturber: Optional[SyntheticRegimeShiftPerturber] = None,
    ):
        self.physics_engine = physics_engine
        self.forecaster = forecaster
        self.regime_checker = regime_checker
        self.perturber = perturber or SyntheticRegimeShiftPerturber(shift_factor=6.0)
        self.gate_evaluator = ReliabilityGateEvaluator(regime_checker=self.regime_checker)
        self.decision_evaluator = DecisionEngineEvaluator()

    def build_snapshot(
        self,
        timestamp: float,
        exchanger_id: str,
        scenario_mode: ReplayMode,
        raw_record: Dict[str, Any],
        causal_history_df: Optional[pd.DataFrame] = None,
    ) -> ReplaySnapshot:
        """
        Builds ReplaySnapshot at timestamp t.
        """
        if exchanger_id not in EXCHANGER_MAPPING:
            raise ValueError(f"Unknown exchanger_id '{exchanger_id}'. Supported: {list(EXCHANGER_MAPPING.keys())}")

        shell_name = EXCHANGER_MAPPING[exchanger_id]
        threshold_cfg = DEFAULT_DECISION_THRESHOLDS.get(exchanger_id, DEFAULT_DECISION_THRESHOLDS["E01"])
        horizon = threshold_cfg.planning_horizon_hours

        required_fields = [
            f"{exchanger_id}_Crude_Tube_T_In_degC",
            f"{exchanger_id}_Crude_Tube_T_Out_degC",
            f"{exchanger_id}_{shell_name}_Shell_T_In_degC",
            f"{exchanger_id}_{shell_name}_Shell_T_Out_degC",
            f"{exchanger_id}_Crude_Tube_m_kg_s",
            f"{exchanger_id}_{shell_name}_Shell_m_kg_s",
        ]

        # Apply perturbation if SHIFTED scenario mode
        eval_record = raw_record
        reason_codes = [ReplayReasonCode.VALID_SNAPSHOT]
        if scenario_mode == ReplayMode.SHIFTED:
            eval_record = self.perturber.perturb_raw_record(raw_record, tag=exchanger_id)
            reason_codes.append(ReplayReasonCode.SHIFTED_SYNTHETIC_STRESS_TEST)

        # 1. M2 Physics State Estimator
        canonical_state = self.physics_engine.process_record(eval_record, exchanger_id)

        # 2. M4 Causal Forecast
        feature_vector = None
        forecast_results: List[ForecastResult] = []

        if causal_history_df is not None and not causal_history_df.empty and self.forecaster is not None and self.forecaster.is_fitted:
            feat_config = FeatureConfig(window_sizes=[6, 24, 72, 168], target_horizon=horizon)
            X_history, _ = extract_causal_features_for_exchanger(causal_history_df, exchanger_id, self.physics_engine, feat_config)

            if not X_history.empty:
                feature_cols = [c for c in X_history.columns if c != "R_f_derived" and not c.startswith("Time_hr")]
                feat_vec = X_history.iloc[-1][feature_cols].fillna(0.0)
                
                if scenario_mode == ReplayMode.SHIFTED:
                    feat_vec = self.perturber.perturb_feature_vector(feat_vec)

                feature_vector = feat_vec
                pred_val = float(self.forecaster.predict(pd.DataFrame([feat_vec]))[0])

                forecast_results.append(
                    ForecastResult(
                        exchanger_id=exchanger_id,
                        timestamp=timestamp,
                        horizon_hours=horizon,
                        prediction=pred_val,
                        input_window_start=timestamp - horizon,
                        input_window_end=timestamp,
                        status=ForecastStatus.SUCCESS,
                        method="RidgeRegression",
                    )
                )

        if not forecast_results:
            reason_codes.append(ReplayReasonCode.FORECAST_UNAVAILABLE)
            # Create explicit FORECAST_UNAVAILABLE result
            forecast_results.append(
                ForecastResult(
                    exchanger_id=exchanger_id,
                    timestamp=timestamp,
                    horizon_hours=horizon,
                    prediction=None,
                    input_window_start=timestamp - horizon,
                    input_window_end=timestamp,
                    status=ForecastStatus.INVALID_CURRENT_STATE,
                    unavailable_reasons=["M4 forecast unavailable for requested timestamp/history"],
                    method="RidgeRegression",
                )
            )

        # 3. M5 Reliability Gate
        forecast_ref_obj = forecast_results[0]
        reliability_res = self.gate_evaluator.evaluate_reliability(
            raw_record=eval_record,
            required_fields=required_fields,
            tag=exchanger_id,
            shell_name=shell_name,
            canonical_state=canonical_state,
            forecast_result=forecast_ref_obj,
            feature_vector=feature_vector,
        )

        # 4. M6 Decision Engine
        decision_res = self.decision_evaluator.evaluate_decision(
            reliability_result=reliability_res,
            canonical_state=canonical_state,
            forecast_results=forecast_results,
            threshold_config=threshold_cfg,
        )

        # Evidence Lineage Reference
        current_rf = canonical_state.fouling.rf_derived if canonical_state.fouling else 0.0
        evidence_ref = {
            "timestamp": timestamp,
            "exchanger_id": exchanger_id,
            "scenario_mode": scenario_mode.value,
            "current_rf_derived": current_rf,
            "ua_current": canonical_state.thermal.ua,
            "ua_clean_ref": canonical_state.thermal.ua_clean_reference,
            "m2_status": canonical_state.data_quality.primary_status.value,
            "m5_gate_status": reliability_res.status.value,
            "m5_failed_checks": [c.check_name for c in reliability_res.checks if c.status == "FAIL"],
            "m6_decision": decision_res.decision.value,
            "human_approval_required": True,
        }

        return ReplaySnapshot(
            timestamp=timestamp,
            exchanger_id=exchanger_id,
            scenario_mode=scenario_mode,
            raw_state_reference=raw_record,
            physics_state=canonical_state,
            forecast_state=forecast_results,
            reliability_state=reliability_res,
            decision_state=decision_res,
            evidence_reference=evidence_ref,
            reason_codes=reason_codes,
            provenance=ReplayProvenance(),
        )
