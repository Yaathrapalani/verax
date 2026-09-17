"""
Main Evaluator for FOUL-X M6.0 Decision Engine.
Orchestrates reliability propagation, trajectory threshold evaluation, and canonical DecisionResult creation.
"""

import math
from typing import Dict, Any, List, Optional
import pandas as pd

from src.physics.schemas import CanonicalExchangerState
from src.forecast.schemas import ForecastResult
from src.foulx.gate.schemas import ReliabilityResult, GateStatus
from src.foulx.decision.reason_codes import DecisionReasonCode, DECISION_REASON_CODE_ORDER
from src.foulx.decision.thresholds import DecisionThresholdConfig, DEFAULT_DECISION_THRESHOLDS
from src.foulx.decision.schemas import (
    DecisionResult,
    DecisionState,
    DecisionProvenance,
)


class DecisionEngineEvaluator:
    """
    FOUL-X M6.0 Decision Engine Evaluator.

    CRITICAL SAFETY INVARIANTS:
    1. If M5 ReliabilityResult status is ABSTAIN, M6 MUST return ABSTAIN.
    2. M6 MUST NEVER issue plant control or shutdown commands.
    3. Human approval invariant is mandatory (`human_approval_required = True`).
    4. Deterministic: identical inputs produce identical DecisionResult.
    """

    def __init__(self, thresholds: Optional[Dict[str, DecisionThresholdConfig]] = None):
        self.thresholds = thresholds or DEFAULT_DECISION_THRESHOLDS

    def evaluate_decision(
        self,
        reliability_result: ReliabilityResult,
        canonical_state: Optional[CanonicalExchangerState],
        forecast_results: List[ForecastResult],
        threshold_config: Optional[DecisionThresholdConfig] = None,
    ) -> DecisionResult:
        """
        Evaluates decision support state for a given exchanger and timestamp.
        Consumes M2 CanonicalExchangerState, M4 ForecastResults, and M5 ReliabilityResult.
        """
        exchanger_id = reliability_result.exchanger_id
        timestamp = reliability_result.timestamp
        config = threshold_config or self.thresholds.get(exchanger_id, DEFAULT_DECISION_THRESHOLDS["E01"])

        reason_codes: List[DecisionReasonCode] = []
        evidence: Dict[str, Any] = {}

        # Extract current Rf_derived from M2 state
        current_rf: Optional[float] = None
        if canonical_state is not None and canonical_state.fouling is not None:
            current_rf = canonical_state.fouling.rf_derived

        # 1. INPUT VALIDATION CHECKS
        # Check invalid threshold
        if not math.isfinite(config.rf_threshold) or config.rf_threshold <= 0.0:
            reason_codes.append(DecisionReasonCode.INVALID_THRESHOLD)

        # Check missing or nonfinite current Rf_derived state
        if current_rf is None or not math.isfinite(current_rf):
            reason_codes.append(DecisionReasonCode.CURRENT_STATE_UNAVAILABLE)

        # Check missing or nonfinite forecast trajectory
        valid_forecasts = [
            f for f in forecast_results
            if f.prediction is not None and math.isfinite(f.prediction)
        ]
        if not valid_forecasts:
            reason_codes.append(DecisionReasonCode.FORECAST_UNAVAILABLE)

        # 2. RELIABILITY PROPAGATION (AUTHORITATIVE M5 GATE INVARIANT)
        if reliability_result.status == GateStatus.ABSTAIN:
            reason_codes.append(DecisionReasonCode.RELIABILITY_ABSTAIN)

        # Filter reason codes to deterministic precedence order
        ordered_reason_codes = [
            code for code in DECISION_REASON_CODE_ORDER if code in reason_codes
        ]

        # If any input validation check or reliability gate failed -> ABSTAIN
        if ordered_reason_codes:
            evidence["abstain_reasons"] = [c.value for c in ordered_reason_codes]
            evidence["m5_reliability_status"] = reliability_result.status.value
            evidence["m5_reason_codes"] = [r.value for r in reliability_result.reason_codes]

            return DecisionResult(
                timestamp=timestamp,
                exchanger_id=exchanger_id,
                decision=DecisionState.ABSTAIN,
                reliability_status=reliability_result.status,
                current_rf_derived=current_rf,
                forecast_horizon_hours=config.planning_horizon_hours,
                threshold_rf=config.rf_threshold,
                threshold_crossing=False,
                estimated_crossing_horizon_hours=None,
                reason_codes=ordered_reason_codes,
                evidence=evidence,
                provenance=DecisionProvenance(),
            )

        # 3. THRESHOLD CROSSING EVALUATION (M5 Passed, Inputs Valid)
        # Filter forecasts within configured planning horizon (e.g. h <= 24)
        planning_forecasts = [
            f for f in valid_forecasts
            if f.horizon_hours <= config.planning_horizon_hours
        ]
        planning_forecasts.sort(key=lambda x: x.horizon_hours)

        crossing_detected = False
        earliest_crossing_h: Optional[int] = None
        crossing_prediction: Optional[float] = None

        for f in planning_forecasts:
            if f.prediction is not None and f.prediction >= config.rf_threshold:
                crossing_detected = True
                earliest_crossing_h = f.horizon_hours
                crossing_prediction = f.prediction
                break

        if crossing_detected:
            final_decision = DecisionState.CLEANING_REVIEW
            ordered_reason_codes = [DecisionReasonCode.THRESHOLD_REACHED]
            evidence["threshold_crossing_details"] = {
                "earliest_crossing_horizon_hours": earliest_crossing_h,
                "predicted_rf": crossing_prediction,
                "configured_threshold_rf": config.rf_threshold,
            }
        else:
            final_decision = DecisionState.OPERATE
            ordered_reason_codes = [DecisionReasonCode.THRESHOLD_NOT_REACHED]
            evidence["threshold_crossing_details"] = {
                "threshold_crossed": False,
                "max_predicted_rf_in_horizon": max([f.prediction for f in planning_forecasts]) if planning_forecasts else None,
                "configured_threshold_rf": config.rf_threshold,
            }

        evidence["m5_reliability_status"] = reliability_result.status.value
        evidence["planning_horizon_hours"] = config.planning_horizon_hours

        return DecisionResult(
            timestamp=timestamp,
            exchanger_id=exchanger_id,
            decision=final_decision,
            reliability_status=reliability_result.status,
            current_rf_derived=current_rf,
            forecast_horizon_hours=config.planning_horizon_hours,
            threshold_rf=config.rf_threshold,
            threshold_crossing=crossing_detected,
            estimated_crossing_horizon_hours=earliest_crossing_h,
            reason_codes=ordered_reason_codes,
            evidence=evidence,
            provenance=DecisionProvenance(),
        )
