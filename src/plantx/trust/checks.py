"""Deterministic checks for Stage 7 Reliability Gate."""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
from src.foulx.gate.checks import (
    check_data_completeness,
    check_sensor_validity,
    check_physics_consistency,
    HistoricalRegimeSupportChecker,
)
from src.plantx.trust.schemas import TrustCheckStatus, TrustReasonCode
from src.physics.schemas import CanonicalExchangerState


class Stage7TrustChecker:
    """Encapsulates deterministic checks for Data Trust, Sensor Validity, Physics, and Regime Support."""

    def __init__(self, regime_checker: Optional[HistoricalRegimeSupportChecker] = None):
        self.regime_checker = regime_checker

    def check_data_trust(self, raw_record: Dict[str, Any], required_fields: List[str]) -> Tuple[TrustCheckStatus, Optional[TrustReasonCode], Dict[str, Any]]:
        res = check_data_completeness(raw_record, required_fields)
        if res.status.value == "PASS":
            return TrustCheckStatus.PASS, None, res.evidence
        return TrustCheckStatus.FAIL, TrustReasonCode.DATA_INCOMPLETE, res.evidence

    def check_sensor_validity(
        self,
        raw_record: Dict[str, Any],
        tag: str,
        shell_name: str,
        sensor_status_signal: Optional[str] = None,
    ) -> Tuple[TrustCheckStatus, Optional[TrustReasonCode], Dict[str, Any]]:
        if sensor_status_signal == "UNKNOWN":
            # UNKNOWN must NOT silently become PASS
            return TrustCheckStatus.UNKNOWN, TrustReasonCode.SENSOR_UNKNOWN, {"status_signal": "UNKNOWN"}
        
        res = check_sensor_validity(raw_record, tag, shell_name)
        if res.status.value == "PASS":
            return TrustCheckStatus.PASS, None, res.evidence
        return TrustCheckStatus.FAIL, TrustReasonCode.SENSOR_INVALID, res.evidence

    def check_physics_consistency(self, canonical_state: CanonicalExchangerState) -> Tuple[TrustCheckStatus, Optional[TrustReasonCode], Dict[str, Any]]:
        res = check_physics_consistency(canonical_state)
        if res.status.value == "PASS":
            return TrustCheckStatus.PASS, None, res.evidence
        return TrustCheckStatus.FAIL, TrustReasonCode.PHYSICS_INCONSISTENT, res.evidence

    def check_regime_support(self, feature_vector: Optional[pd.Series]) -> Tuple[TrustCheckStatus, Optional[TrustReasonCode], Dict[str, Any]]:
        if self.regime_checker is None or feature_vector is None:
            return TrustCheckStatus.UNKNOWN, TrustReasonCode.REGIME_UNSUPPORTED, {"reason": "Regime checker or feature vector unavailable"}
        
        res = self.regime_checker.check_regime_support(feature_vector)
        if res.status.value == "PASS":
            return TrustCheckStatus.SUPPORTED, None, res.evidence
        return TrustCheckStatus.UNSUPPORTED, TrustReasonCode.REGIME_UNSUPPORTED, res.evidence
