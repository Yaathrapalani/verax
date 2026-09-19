"""Prediction Challenge Engine and Reliability Gate Evaluator for Stage 7."""

from typing import Dict, Any, List, Optional
import pandas as pd
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.intelligence.schemas import FoulingPrognosis
from src.plantx.trust.schemas import (
    ReliabilityAssessment,
    OverallTrustState,
    TrustCheckStatus,
    TrustReasonCode,
    REASON_CODE_PRECEDENCE,
    PredictionInterval,
    SafetyViolationError,
)
from src.plantx.trust.checks import Stage7TrustChecker
from src.physics.schemas import CanonicalExchangerState


class Stage7ReliabilityGate:
    """Master Reliability Gate evaluating predictions and establishing permission boundaries."""

    def __init__(self, trust_checker: Optional[Stage7TrustChecker] = None):
        self.trust_checker = trust_checker or Stage7TrustChecker()

    def evaluate(
        self,
        prognosis: FoulingPrognosis,
        raw_record: Dict[str, Any],
        required_fields: List[str],
        tag: str,
        shell_name: str,
        canonical_state: CanonicalExchangerState,
        feature_vector: Optional[pd.Series] = None,
        sensor_status_signal: Optional[str] = None,
        prediction_interval: Optional[PredictionInterval] = None,
        allow_autonomous_execution: bool = False,
    ) -> ReliabilityAssessment:
        # Check human safety control invariant
        if allow_autonomous_execution:
            raise SafetyViolationError("Autonomous process control is strictly forbidden under the PLANT-X Safety Constitution!")

        # Execute challenges
        d_status, d_reason, d_ev = self.trust_checker.check_data_trust(raw_record, required_fields)
        s_status, s_reason, s_ev = self.trust_checker.check_sensor_validity(raw_record, tag, shell_name, sensor_status_signal)
        p_status, p_reason, p_ev = self.trust_checker.check_physics_consistency(canonical_state)
        r_status, r_reason, r_ev = self.trust_checker.check_regime_support(feature_vector)

        # Collect failing reasons
        unfiltered_reasons: List[TrustReasonCode] = []
        if d_reason: unfiltered_reasons.append(d_reason)
        if s_reason: unfiltered_reasons.append(s_reason)
        if p_reason: unfiltered_reasons.append(p_reason)
        if r_reason: unfiltered_reasons.append(r_reason)

        if prognosis.prediction is None:
            unfiltered_reasons.append(TrustReasonCode.FORECAST_UNAVAILABLE)

        # Sort reasons deterministically
        ordered_reasons = [r for r in REASON_CODE_PRECEDENCE if r in unfiltered_reasons]

        regime_ok = (r_status == TrustCheckStatus.SUPPORTED or r_status == TrustCheckStatus.PASS or (r_status == TrustCheckStatus.UNKNOWN and feature_vector is None))

        all_passed = (
            d_status == TrustCheckStatus.PASS and
            s_status == TrustCheckStatus.PASS and
            p_status == TrustCheckStatus.PASS and
            regime_ok and
            prognosis.prediction is not None
        )

        if all_passed:
            overall_state = OverallTrustState.TRUSTED
            permission = True
        else:
            overall_state = OverallTrustState.ABSTAIN
            permission = False

        prov = Provenance(
            provenance_id=f"prov-trust-{prognosis.asset_id}-{int(prognosis.timestamp)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="Stage7ReliabilityGate",
            timestamp="2026-09-17T13:56:00Z",
            transformation_applied="Stage 7 Trust & Reliability Assessment",
        )

        return ReliabilityAssessment(
            assessment_id=f"trust-assess-{prognosis.asset_id}-{int(prognosis.timestamp)}",
            asset_id=prognosis.asset_id,
            timestamp=prognosis.timestamp,
            forecast_reference=prognosis.model_dump(),
            data_status=d_status,
            sensor_status=s_status,
            physics_status=p_status,
            regime_status=r_status,
            uncertainty_status=prognosis.uncertainty_status,
            calibration_status=prediction_interval.calibration_status if prediction_interval else "UNCALIBRATED",
            prediction_interval=prediction_interval,
            overall_state=overall_state,
            decision_permission=permission,
            fallback_policy="FIXED_TIME_BASED_MAINTENANCE_POLICY",
            reason_codes=ordered_reasons,
            check_details={
                "data": d_ev,
                "sensor": s_ev,
                "physics": p_ev,
                "regime": r_ev,
            },
            provenance=prov,
        )
