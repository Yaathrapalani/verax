"""
Reason codes for FOUL-X M9.0 Deterministic Replay Engine.
"""

from enum import Enum


class ReplayReasonCode(str, Enum):
    """
    Reason codes for Replay operations & boundary conditions.
    """
    VALID_SNAPSHOT = "VALID_SNAPSHOT"
    INVALID_TIMESTAMP = "INVALID_TIMESTAMP"
    TIMESTAMP_OUT_OF_RANGE = "TIMESTAMP_OUT_OF_RANGE"
    MISSING_EXCHANGER = "MISSING_EXCHANGER"
    INVALID_SCENARIO = "INVALID_SCENARIO"
    FORECAST_UNAVAILABLE = "FORECAST_UNAVAILABLE"
    SHIFTED_SYNTHETIC_STRESS_TEST = "SHIFTED_SYNTHETIC_STRESS_TEST"
