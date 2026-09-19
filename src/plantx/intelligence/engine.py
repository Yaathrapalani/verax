"""Engine and Evaluator for Stage 6 Intelligence Core."""

import hashlib
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.shadow.schemas import DigitalShadowSnapshot
from src.plantx.engineering.domains.heat_exchanger import HeatExchangerStateBuilder
from src.plantx.graph.evidence_graph import EvidenceGraph, EvidenceEdgeType
from src.plantx.intelligence.schemas import (
    FoulingState,
    FoulingPrognosis,
    ForecastStatus,
    ModelStatus,
)
from src.forecast.baselines import PersistenceBaseline, RecentTrendBaseline
from src.foulx.replay import ReplayService
from src.physics.state_estimator import PhysicsStateEstimator
from src.models.features import extract_causal_features_for_exchanger
from src.models.schemas import FeatureConfig
from src.models.ridge_forecaster import RidgeFoulingForecaster
from src.forecast.metrics import evaluate_forecast_predictions


class IntelligenceEngine:
    """Master Stage 6 Intelligence Engine generating FoulingState and FoulingPrognosis."""

    def __init__(self, replay_service: Optional[ReplayService] = None):
        self.replay_service = replay_service or ReplayService()
        self.hx_builder = HeatExchangerStateBuilder(replay_service=self.replay_service)
        self.persistence = PersistenceBaseline()
        self.recent_trend = RecentTrendBaseline(trend_window_hours=24)

    def compute_fouling_state(
        self,
        asset_id: str,
        shadow_snapshot: DigitalShadowSnapshot,
    ) -> FoulingState:
        """Constructs canonical FoulingState representation for asset at time T."""
        eng_state = self.hx_builder.build_heat_exchanger_state(asset_id, shadow_snapshot)
        rf_qty = eng_state.quantities.get("Rf_derived")
        
        current_rf = rf_qty.normalized_value if (rf_qty and rf_qty.status == "VALID") else None
        
        # Historical context calculation
        history_df = self.replay_service.resolver.resolve_causal_history(
            shadow_snapshot.target_time,
            window_hours=168,
        )
        
        recent_delta_rf = None
        growth_rate = None
        if not history_df.empty and len(history_df) > 1 and "R_f_derived" in history_df.columns:
            valid_rf = history_df["R_f_derived"].dropna()
            if len(valid_rf) >= 2:
                recent_delta_rf = float(valid_rf.iloc[-1] - valid_rf.iloc[0])
                time_diff = float(valid_rf.index[-1] - valid_rf.index[0])
                if time_diff > 0:
                    growth_rate = recent_delta_rf / time_diff

        prov = Provenance(
            provenance_id=f"prov-foulstate-{asset_id}-{int(shadow_snapshot.target_time)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="IntelligenceEngine.compute_fouling_state",
            timestamp="2026-09-17T13:48:00Z",
            transformation_applied="Stage 6 Fouling State Construction",
        )

        return FoulingState(
            asset_id=asset_id,
            timestamp=shadow_snapshot.target_time,
            current_rf_derived=current_rf,
            recent_delta_rf=recent_delta_rf,
            recent_growth_rate=growth_rate,
            historical_context_hours=168.0,
            status="VALID" if current_rf is not None else "UNAVAILABLE",
            truth_state=TruthState.INFERRED if current_rf is not None else TruthState.UNRESOLVED,
            provenance=prov,
        )

    def forecast(
        self,
        asset_id: str,
        timestamp: float,
        horizon_hours: int = 24,
        model_id: str = "Ridge",
    ) -> FoulingPrognosis:
        """
        Executes forecast for asset_id at timestamp for horizon_hours.
        Enforces strict temporal causality t_observed <= timestamp.
        """
        # Validate timestamp within available bounds
        t_min, t_max = self.replay_service.resolver.get_min_max_timestamps()
        if timestamp < t_min or timestamp > t_max:
            prov = Provenance(
                provenance_id=f"prov-prog-err-{asset_id}-{int(timestamp)}",
                provenance_type=ProvenanceType.CALCULATION,
                source_reference="IntelligenceEngine.forecast",
                timestamp="2026-09-17T13:48:00Z",
                transformation_applied="Stage 6 Forecast Execution (Invalid)",
            )
            return FoulingPrognosis(
                prognosis_id=f"prog-invalid-{asset_id}-{int(timestamp)}-{horizon_hours}h",
                asset_id=asset_id,
                timestamp=timestamp,
                horizon_hours=horizon_hours,
                target_definition="R_f_derived(t+h)",
                prediction=None,
                model_id=model_id,
                status=ForecastStatus.INVALID_INPUT,
                uncertainty_status="NOT_IMPLEMENTED",
                mechanism_claim="NONE",
                provenance=prov,
            )

        # Causal history extraction
        causal_history = self.replay_service.resolver.resolve_causal_history(
            timestamp,
            window_hours=168,
        )

        prov = Provenance(
            provenance_id=f"prov-prog-{asset_id}-{int(timestamp)}-{horizon_hours}h",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="IntelligenceEngine.forecast",
            timestamp="2026-09-17T13:48:00Z",
            transformation_applied=f"Stage 6 {model_id} Forecast Execution",
        )

        # Check history sufficiency
        if len(causal_history) < 24:
            return FoulingPrognosis(
                prognosis_id=f"prog-insufficient-{asset_id}-{int(timestamp)}-{horizon_hours}h",
                asset_id=asset_id,
                timestamp=timestamp,
                horizon_hours=horizon_hours,
                target_definition="R_f_derived(t+h)",
                prediction=None,
                model_id=model_id,
                status=ForecastStatus.INSUFFICIENT_HISTORY,
                uncertainty_status="NOT_IMPLEMENTED",
                mechanism_claim="NONE",
                provenance=prov,
            )

        rf_series = None
        if "R_f_derived" in causal_history.columns:
            rf_series = causal_history["R_f_derived"]
        else:
            # Derive Rf series using PhysicsStateEstimator on causal history for asset_id
            rf_values = []
            timestamps = []
            for t_idx, row in causal_history.iterrows():
                t_row = float(row["Time_hr"])
                raw_rec = row.to_dict()
                phys_st = self.replay_service.physics_engine.process_record(raw_rec, exchanger_id=asset_id)
                rf_values.append(phys_st.fouling.rf_derived)
                timestamps.append(t_row)
            rf_series = pd.Series(rf_values, index=timestamps).dropna()

        pers_res = self.persistence.predict(rf_series, timestamp, horizon_hours, asset_id)

        if model_id == "Persistence":
            return FoulingPrognosis(
                prognosis_id=f"prog-pers-{asset_id}-{int(timestamp)}-{horizon_hours}h",
                asset_id=asset_id,
                timestamp=timestamp,
                horizon_hours=horizon_hours,
                prediction=pers_res.prediction,
                model_id="Persistence",
                status=ForecastStatus.AVAILABLE if pers_res.prediction is not None else ForecastStatus.UNAVAILABLE,
                baseline_reference={"persistence_pred": pers_res.prediction},
                uncertainty_status="NOT_IMPLEMENTED",
                mechanism_claim="NONE",
                provenance=prov,
            )

        elif model_id == "RecentTrend":
            trend_res = self.recent_trend.predict(rf_series, timestamp, horizon_hours, asset_id)
            return FoulingPrognosis(
                prognosis_id=f"prog-trend-{asset_id}-{int(timestamp)}-{horizon_hours}h",
                asset_id=asset_id,
                timestamp=timestamp,
                horizon_hours=horizon_hours,
                prediction=trend_res.prediction,
                model_id="RecentTrend",
                status=ForecastStatus.AVAILABLE if trend_res.prediction is not None else ForecastStatus.UNAVAILABLE,
                baseline_reference={"persistence_pred": pers_res.prediction},
                uncertainty_status="NOT_IMPLEMENTED",
                mechanism_claim="NONE",
                provenance=prov,
            )

        elif model_id == "Ridge":
            f_snap = self.replay_service.get_snapshot(timestamp, exchanger_id=asset_id)
            prediction = None
            status = ForecastStatus.UNAVAILABLE
            
            if f_snap.forecast_state and len(f_snap.forecast_state) > 0:
                fc = f_snap.forecast_state[0]
                prediction = fc.prediction
                status = ForecastStatus.AVAILABLE if prediction is not None else ForecastStatus.UNAVAILABLE

            return FoulingPrognosis(
                prognosis_id=f"prog-ridge-{asset_id}-{int(timestamp)}-{horizon_hours}h",
                asset_id=asset_id,
                timestamp=timestamp,
                horizon_hours=horizon_hours,
                prediction=prediction,
                model_id="Ridge",
                status=status,
                baseline_reference={"persistence_pred": pers_res.prediction},
                uncertainty_status="NOT_IMPLEMENTED",
                mechanism_claim="NONE",
                provenance=prov,
            )

        else:
            return FoulingPrognosis(
                prognosis_id=f"prog-unknown-{asset_id}-{int(timestamp)}-{horizon_hours}h",
                asset_id=asset_id,
                timestamp=timestamp,
                horizon_hours=horizon_hours,
                prediction=None,
                model_id=model_id,
                status=ForecastStatus.UNAVAILABLE,
                uncertainty_status="NOT_IMPLEMENTED",
                mechanism_claim="NONE",
                provenance=prov,
            )


class IntelligenceEvidenceBridge:
    """Connects Stage 6 FoulingPrognosis backward to Stage 4 Evidence Graph."""

    @staticmethod
    def attach_prognosis_to_graph(
        graph: EvidenceGraph,
        prognosis: FoulingPrognosis,
        state_node_id: str,
    ) -> str:
        prog_node_id = prognosis.prognosis_id
        graph.add_node(
            node_id=prog_node_id,
            node_type="Prediction",
            truth_state=TruthState.INFERRED.value if prognosis.prediction is not None else TruthState.UNRESOLVED.value,
            payload=prognosis.model_dump(),
        )
        graph.add_edge(
            source_id=state_node_id,
            target_id=prog_node_id,
            edge_type=EvidenceEdgeType.PREDICTS,
        )
        return prog_node_id


class ModelEvaluator:
    """Evaluates forecast models strictly on designated validation or test splits."""

    @staticmethod
    def evaluate_model_on_split(
        df_all: pd.DataFrame,
        exchanger_id: str,
        horizon_hours: int,
        split: str = "validation",
    ) -> Dict[str, float]:
        """
        Evaluates model metrics (MAE, RMSE, MBE, R2) on validation or test split.
        Split boundaries:
        Train: t <= 44,799
        Validation: 44,800 <= t <= 54,399
        Test: 54,400 <= t <= 63,999
        """
        if split == "validation":
            split_mask = (df_all["Time_hr"] >= 44800) & (df_all["Time_hr"] <= 54399)
        elif split == "test":
            split_mask = (df_all["Time_hr"] >= 54400) & (df_all["Time_hr"] <= 63999)
        else:
            raise ValueError(f"Unsupported split '{split}'")

        df_sub = df_all.loc[df_all["exchanger_id"] == exchanger_id].copy() if "exchanger_id" in df_all.columns else df_all.copy()
        
        if "R_f_derived" in df_sub.columns:
            rf_series = df_sub["R_f_derived"]
        else:
            phys_engine = PhysicsStateEstimator()
            phys_engine.fit_baseline_from_dataframe(df_all)
            rf_vals = []
            for _, row in df_sub.iterrows():
                st = phys_engine.process_record(row.to_dict(), exchanger_id)
                rf_vals.append(st.fouling.rf_derived)
            rf_series = pd.Series(rf_vals, index=df_sub.index)

        target = rf_series.shift(-horizon_hours)
        preds = rf_series  # Persistence baseline

        eval_mask = split_mask & target.notna() & preds.notna()
        y_true = target.loc[eval_mask].values
        y_pred = preds.loc[eval_mask].values

        res = evaluate_forecast_predictions(y_true, y_pred)
        return res

    @staticmethod
    def evaluate_candidate_promotion(
        val_metrics_baseline: Dict[str, float],
        val_metrics_candidate: Dict[str, float],
        selection_split: str = "validation",
    ) -> ModelStatus:
        """
        Determines promotion eligibility strictly from VALIDATION metrics.
        Fails if selected from test split.
        """
        if selection_split == "test":
            # REJECT: Model selection using test split is strictly forbidden
            return ModelStatus.REJECTED

        if val_metrics_candidate.get("mae", float("inf")) < val_metrics_baseline.get("mae", float("inf")):
            return ModelStatus.PROMOTED
        return ModelStatus.REJECTED
