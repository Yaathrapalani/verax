"""Calculation contracts, registry, and execution models for Stage 5 Engineering Core."""

from typing import Dict, Any, List, Optional, Callable, Tuple
from pydantic import BaseModel, Field
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance
from src.plantx.engineering.quantities import EngineeringQuantity, QuantityStatus


class CalculationDefinition(BaseModel):
    """Declarative contract for an engineering calculation."""
    calculation_id: str = Field(..., description="Unique calculation identifier")
    name: str = Field(..., description="Calculation name")
    description: str = Field(..., description="Detailed engineering description")
    equation_identifier: str = Field(..., description="Equation / formulation reference")
    required_inputs: List[str] = Field(..., description="List of required input parameter names")
    output_parameter: str = Field(..., description="Output parameter name")
    assumptions: List[str] = Field(default_factory=list, description="Explicit assumptions")
    calculation_version: str = Field("1.0.0", description="Calculation version")


class CalculationExecutionResult(BaseModel):
    """Result emitted by executing a registered calculation."""
    execution_id: str
    calculation_id: str
    target_time: float
    inputs_used: Dict[str, Any]
    output_quantity: EngineeringQuantity
    status: str  # COMPUTED, INSUFFICIENT_DATA, DIMENSION_MISMATCH, INCONSISTENT
    assumptions: List[str]
    provenance: Provenance


class CalculationRegistry:
    """Registry managing and safely executing trusted engineering calculations."""

    _registry: Dict[str, Tuple[CalculationDefinition, Callable[[Dict[str, EngineeringQuantity], float, Provenance], EngineeringQuantity]]] = {}

    @classmethod
    def register_calculation(
        cls,
        definition: CalculationDefinition,
        fn: Callable[[Dict[str, EngineeringQuantity], float, Provenance], EngineeringQuantity],
    ) -> None:
        cls._registry[definition.calculation_id] = (definition, fn)

    @classmethod
    def get_calculation(cls, calculation_id: str) -> Optional[CalculationDefinition]:
        if calculation_id in cls._registry:
            return cls._registry[calculation_id][0]
        return None

    @classmethod
    def list_calculations(cls) -> List[CalculationDefinition]:
        return [defn for defn, _ in cls._registry.values()]

    @classmethod
    def execute_calculation(
        cls,
        calculation_id: str,
        inputs: Dict[str, EngineeringQuantity],
        target_time: float,
        provenance: Provenance,
    ) -> CalculationExecutionResult:
        if calculation_id not in cls._registry:
            raise ValueError(f"Calculation '{calculation_id}' is not registered.")

        defn, fn = cls._registry[calculation_id]

        # Check required inputs
        missing = [inp for inp in defn.required_inputs if inp not in inputs or inputs[inp].status != QuantityStatus.VALID]
        if missing:
            empty_qty = EngineeringQuantity(
                quantity_id=f"qty-missing-{calculation_id}",
                name=defn.output_parameter,
                status=QuantityStatus.UNAVAILABLE,
                truth_state=TruthState.UNRESOLVED,
                provenance=provenance,
            )
            return CalculationExecutionResult(
                execution_id=f"exec-{calculation_id}-{int(target_time)}",
                calculation_id=calculation_id,
                target_time=target_time,
                inputs_used={k: v.model_dump() for k, v in inputs.items()},
                output_quantity=empty_qty,
                status="INSUFFICIENT_DATA",
                assumptions=defn.assumptions,
                provenance=provenance,
            )

        # Execute trusted calculation function
        output_qty = fn(inputs, target_time, provenance)
        output_qty.assumptions.extend(defn.assumptions)
        output_qty.calculation_ref = calculation_id

        return CalculationExecutionResult(
            execution_id=f"exec-{calculation_id}-{int(target_time)}",
            calculation_id=calculation_id,
            target_time=target_time,
            inputs_used={k: v.model_dump() for k, v in inputs.items()},
            output_quantity=output_qty,
            status="COMPUTED",
            assumptions=defn.assumptions,
            provenance=provenance,
        )
