"""
Reason codes for FOUL-X M5.0 Reliability Gate.
Defines explicit string constants and deterministic evaluation order.
"""

from enum import Enum
from typing import List


class ReliabilityReasonCode(str, Enum):
    """
    Deterministic reason codes for Reliability Gate checks.
    Order of precedence for deterministic reporting:
    1. DATA_INCOMPLETE
    2. SENSOR_INVALID
    3. PHYSICS_INCONSISTENT
    4. REGIME_OOD
    """
    DATA_INCOMPLETE = "DATA_INCOMPLETE"
    SENSOR_INVALID = "SENSOR_INVALID"
    PHYSICS_INCONSISTENT = "PHYSICS_INCONSISTENT"
    REGIME_OOD = "REGIME_OOD"


REASON_CODE_ORDER: List[ReliabilityReasonCode] = [
    ReliabilityReasonCode.DATA_INCOMPLETE,
    ReliabilityReasonCode.SENSOR_INVALID,
    ReliabilityReasonCode.PHYSICS_INCONSISTENT,
    ReliabilityReasonCode.REGIME_OOD,
]
