"""
Reason codes for FOUL-X M6.0 Decision Engine.
Defines explicit string constants and deterministic evaluation precedence.
"""

from enum import Enum
from typing import List


class DecisionReasonCode(str, Enum):
    """
    Deterministic reason codes for Decision Engine evaluations.
    Order of precedence for deterministic reporting:
    1. RELIABILITY_ABSTAIN
    2. FORECAST_UNAVAILABLE
    3. CURRENT_STATE_UNAVAILABLE
    4. INVALID_THRESHOLD
    5. THRESHOLD_REACHED
    6. THRESHOLD_NOT_REACHED
    """
    RELIABILITY_ABSTAIN = "RELIABILITY_ABSTAIN"
    FORECAST_UNAVAILABLE = "FORECAST_UNAVAILABLE"
    CURRENT_STATE_UNAVAILABLE = "CURRENT_STATE_UNAVAILABLE"
    INVALID_THRESHOLD = "INVALID_THRESHOLD"
    THRESHOLD_REACHED = "THRESHOLD_REACHED"
    THRESHOLD_NOT_REACHED = "THRESHOLD_NOT_REACHED"


DECISION_REASON_CODE_ORDER: List[DecisionReasonCode] = [
    DecisionReasonCode.RELIABILITY_ABSTAIN,
    DecisionReasonCode.FORECAST_UNAVAILABLE,
    DecisionReasonCode.CURRENT_STATE_UNAVAILABLE,
    DecisionReasonCode.INVALID_THRESHOLD,
    DecisionReasonCode.THRESHOLD_REACHED,
    DecisionReasonCode.THRESHOLD_NOT_REACHED,
]
