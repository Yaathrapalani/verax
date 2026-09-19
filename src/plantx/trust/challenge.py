"""Prediction Challenge Engine for Stage 7."""

from typing import Dict, Any, List, Optional
import pandas as pd
from src.plantx.intelligence.schemas import FoulingPrognosis
from src.plantx.trust.schemas import TrustCheckStatus, TrustReasonCode
from src.plantx.trust.checks import Stage7TrustChecker
from src.physics.schemas import CanonicalExchangerState


class PredictionChallengeEngine:
    """Challenges predictions across 5 explicit dimensions without causal inference."""

    def __init__(self, trust_checker: Optional[Stage7TrustChecker] = None):
        self.trust_checker = trust_checker or Stage7TrustChecker()

    def challenge_prediction(
        self,
        prognosis: FoulingPrognosis,
        raw_record: Dict[str, Any],
        required_fields: List[str],
        tag: str,
        shell_name: str,
        canonical_state: CanonicalExchangerState,
        feature_vector: Optional[pd.Series] = None,
        sensor_status_signal: Optional[str] = None,
    ) -> Dict[str, Any]:
        d_st, d_r, d_ev = self.trust_checker.check_data_trust(raw_record, required_fields)
        s_st, s_r, s_ev = self.trust_checker.check_sensor_validity(raw_record, tag, shell_name, sensor_status_signal)
        p_st, p_r, p_ev = self.trust_checker.check_physics_consistency(canonical_state)
        r_st, r_r, r_ev = self.trust_checker.check_regime_support(feature_vector)
        
        u_st = TrustCheckStatus.PASS if prognosis.uncertainty_status != "EXCESSIVE" else TrustCheckStatus.FAIL

        return {
            "data_challenge": {"status": d_st.value, "reason": d_r.value if d_r else None, "evidence": d_ev},
            "sensor_challenge": {"status": s_st.value, "reason": s_r.value if s_r else None, "evidence": s_ev},
            "physics_challenge": {"status": p_st.value, "reason": p_r.value if p_r else None, "evidence": p_ev},
            "regime_challenge": {"status": r_st.value, "reason": r_r.value if r_r else None, "evidence": r_ev},
            "uncertainty_challenge": {"status": u_st.value, "reason": None, "evidence": {"status": prognosis.uncertainty_status}},
        }
