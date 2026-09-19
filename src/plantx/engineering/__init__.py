"""Module exports for Stage 5 Engineering Core."""

from src.plantx.engineering.dimensions import DimensionCategory, EngineeringUnitRegistry
from src.plantx.engineering.quantities import QuantityStatus, EngineeringQuantity
from src.plantx.engineering.contracts import (
    CalculationDefinition,
    CalculationExecutionResult,
    CalculationRegistry,
)
from src.plantx.engineering.state import EngineeringState
from src.plantx.engineering.domains.heat_exchanger import HeatExchangerStateBuilder
from src.plantx.engineering.evidence_bridge import EngineeringEvidenceBridge

__all__ = [
    "DimensionCategory",
    "EngineeringUnitRegistry",
    "QuantityStatus",
    "EngineeringQuantity",
    "CalculationDefinition",
    "CalculationExecutionResult",
    "CalculationRegistry",
    "EngineeringState",
    "HeatExchangerStateBuilder",
    "EngineeringEvidenceBridge",
]
