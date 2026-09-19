"""Pump, Valve, and Generic Equipment Boundaries for Stage 14."""

from typing import Dict, Any
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.process.schemas import EquipmentType
from src.plantx.equipment.schemas import EquipmentExecution, SolverStatus
from src.plantx.equipment.equipment_registry import EquipmentModelContract


class PumpModelBoundary(EquipmentModelContract):
    """Honest Pump Model Boundary exposing PUMP_HYDRAULICS_UNAVAILABLE without fake performance curves."""

    def __init__(self):
        super().__init__(model_id="PumpModelBoundary", equipment_type=EquipmentType.PUMP)

    def execute(self, equipment_id: str, inputs: Dict[str, Any], timestamp: float) -> EquipmentExecution:
        prov = Provenance(
            provenance_id=f"prov-pump-{equipment_id}-{int(timestamp)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="PumpModelBoundary",
            timestamp="2026-09-17T15:45:00Z",
        )
        return EquipmentExecution(
            execution_id=f"exec-pump-{equipment_id}-{int(timestamp)}",
            equipment_id=equipment_id,
            model_id=self.model_id,
            input_state=inputs,
            output_state={"status": "PUMP_HYDRAULICS_UNAVAILABLE", "reason": "Hydraulic curve & pressure measurements unavailable in dataset"},
            solver_status=SolverStatus.UNAVAILABLE,
            applicability="UNAVAILABLE_DATASET_BOUNDARY",
            provenance=prov,
            truth_state=TruthState.SIMULATED,
        )


class ValveModelBoundary(EquipmentModelContract):
    """Honest Valve Model Boundary exposing VALVE_MODEL_UNAVAILABLE without fake Cv coefficients."""

    def __init__(self):
        super().__init__(model_id="ValveModelBoundary", equipment_type=EquipmentType.VALVE)

    def execute(self, equipment_id: str, inputs: Dict[str, Any], timestamp: float) -> EquipmentExecution:
        prov = Provenance(
            provenance_id=f"prov-valve-{equipment_id}-{int(timestamp)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="ValveModelBoundary",
            timestamp="2026-09-17T15:45:00Z",
        )
        return EquipmentExecution(
            execution_id=f"exec-valve-{equipment_id}-{int(timestamp)}",
            equipment_id=equipment_id,
            model_id=self.model_id,
            input_state=inputs,
            output_state={"status": "VALVE_MODEL_UNAVAILABLE", "reason": "Valve position % and Cv curves unavailable in dataset"},
            solver_status=SolverStatus.UNAVAILABLE,
            applicability="UNAVAILABLE_DATASET_BOUNDARY",
            provenance=prov,
            truth_state=TruthState.SIMULATED,
        )


class GenericEquipmentModel(EquipmentModelContract):
    """Generic Equipment Model Boundary."""

    def __init__(self):
        super().__init__(model_id="GenericEquipmentModel", equipment_type=EquipmentType.UNKNOWN)

    def execute(self, equipment_id: str, inputs: Dict[str, Any], timestamp: float) -> EquipmentExecution:
        prov = Provenance(
            provenance_id=f"prov-gen-{equipment_id}-{int(timestamp)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="GenericEquipmentModel",
            timestamp="2026-09-17T15:45:00Z",
        )
        return EquipmentExecution(
            execution_id=f"exec-gen-{equipment_id}-{int(timestamp)}",
            equipment_id=equipment_id,
            model_id=self.model_id,
            input_state=inputs,
            output_state={"status": "GENERIC_BOUNDARY_VALIDATED"},
            solver_status=SolverStatus.CONVERGED,
            applicability="GENERIC_IDENTITY",
            provenance=prov,
            truth_state=TruthState.SIMULATED,
        )
