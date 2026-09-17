"""
Reason codes for FOUL-X M7.0 Evaluation Experiment.
Defines explicit string constants and evaluation reason codes.
"""

from enum import Enum
from typing import List


class EvaluationReasonCode(str, Enum):
    """
    Deterministic reason codes for M7.0 Policy Evaluation outcomes.
    """
    TEST_SPLIT_EVALUATED = "TEST_SPLIT_EVALUATED"
    SHIFTED_REGIME_OOD_TRIGGERED = "SHIFTED_REGIME_OOD_TRIGGERED"
    FALLBACK_TO_FIXED_POLICY = "FALLBACK_TO_FIXED_POLICY"
    UNGATED_AI_ACTION_ALLOWED = "UNGATED_AI_ACTION_ALLOWED"
    GATED_AI_ACTION_ALLOWED = "GATED_AI_ACTION_ALLOWED"
    GROUND_TRUTH_EVALUATED_ONLY = "GROUND_TRUTH_EVALUATED_ONLY"
