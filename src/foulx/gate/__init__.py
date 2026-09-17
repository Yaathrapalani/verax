"""
FOUL-X M5.0 Reliability Gate Module Initializer.
Exposes public schema, reason code, and evaluator interfaces.
"""

from src.foulx.gate.reason_codes import ReliabilityReasonCode, REASON_CODE_ORDER
from src.foulx.gate.schemas import (
    GateStatus,
    CheckStatus,
    CheckResult,
    ForecastReference,
    GateProvenance,
    ReliabilityResult,
)
from src.foulx.gate.checks import (
    check_data_completeness,
    check_sensor_validity,
    check_physics_consistency,
    HistoricalRegimeSupportChecker,
)
from src.foulx.gate.evaluator import ReliabilityGateEvaluator

__all__ = [
    "ReliabilityReasonCode",
    "REASON_CODE_ORDER",
    "GateStatus",
    "CheckStatus",
    "CheckResult",
    "ForecastReference",
    "GateProvenance",
    "ReliabilityResult",
    "check_data_completeness",
    "check_sensor_validity",
    "check_physics_consistency",
    "HistoricalRegimeSupportChecker",
    "ReliabilityGateEvaluator",
]
