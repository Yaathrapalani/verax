"""
FOUL-X Physics State Estimator Package.
Provides deterministic thermodynamic calculations, typed canonical state schemas,
validity checking, and batch/single-record state estimation.
"""

from src.physics.schemas import (
    StateValidity,
    ThermalState,
    FoulingState,
    DataQualityState,
    AvailabilityState,
    ProvenanceState,
    CanonicalExchangerState,
)
from src.physics.equations import (
    calculate_heat_duty_tube,
    calculate_heat_duty_shell,
    calculate_lmtd,
    calculate_ua,
    calculate_rf_derived,
    calculate_thermal_discrepancy,
)
from src.physics.validators import validate_physics_inputs
from src.physics.state_estimator import PhysicsStateEstimator

__all__ = [
    "StateValidity",
    "ThermalState",
    "FoulingState",
    "DataQualityState",
    "AvailabilityState",
    "ProvenanceState",
    "CanonicalExchangerState",
    "calculate_heat_duty_tube",
    "calculate_heat_duty_shell",
    "calculate_lmtd",
    "calculate_ua",
    "calculate_rf_derived",
    "calculate_thermal_discrepancy",
    "validate_physics_inputs",
    "PhysicsStateEstimator",
]
