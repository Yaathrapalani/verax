"""Master Stage 14 Equipment Runtime and ProcessGraph Orchestrator."""

import hashlib
from typing import Dict, Any, Optional
from pathlib import Path

from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.process.schemas import PlantModel
from src.plantx.process.graph import PlantGraph
from src.plantx.equipment.schemas import EquipmentExecution, EquipmentReplaySnapshot
from src.plantx.equipment.equipment_registry import EquipmentRegistry
from src.plantx.equipment.heat_exchanger.model import HeatExchangerModel
from src.plantx.equipment.boundaries import PumpModelBoundary, ValveModelBoundary, GenericEquipmentModel
from src.plantx.equipment.errors import (
    TemporalEquipmentViolation,
    EquipmentSourceMutation,
    AutonomousControlViolationError,
)


class EquipmentRuntime:
    """Master Equipment Simulation Runtime."""

    def __init__(self):
        self.registry = EquipmentRegistry()
        self.registry.register_model(HeatExchangerModel())
        self.registry.register_model(PumpModelBoundary())
        self.registry.register_model(ValveModelBoundary())
        self.registry.register_model(GenericEquipmentModel())

    def execute_equipment_simulation(
        self,
        plant_model: PlantModel,
        equipment_id: str,
        timestamp: float,
        model_id: str = "HeatExchangerModel",
        inputs_override: Optional[Dict[str, Any]] = None,
        baseline_max_time: float = 63999.0,
        data_path: Path = Path("data/raw/heat_exchanger_fouling_dataset.csv"),
        allow_autonomous_control: bool = False,
    ) -> EquipmentExecution:
        if allow_autonomous_control:
            raise AutonomousControlViolationError("Autonomous control strictly forbidden.")

        h_before = hashlib.sha256(data_path.read_bytes()).hexdigest()

        if timestamp > baseline_max_time:
            raise TemporalEquipmentViolation(f"Timestamp {timestamp} exceeds baseline max time {baseline_max_time}")

        model = self.registry.get_model(model_id)
        if not model:
            raise ValueError(f"Equipment model {model_id} not registered.")

        # Extract inputs from PlantModel equipment entity if not overridden
        inputs = inputs_override or {}
        if not inputs and equipment_id in plant_model.equipment:
            eq = plant_model.equipment[equipment_id]
            # Populate default thermal inputs from E-102 context if available
            if equipment_id == "E-102":
                inputs = {
                    "T_in_h": 220.0,
                    "T_out_h": 170.0,
                    "T_in_c": 150.0,
                    "T_out_c": 190.0,
                    "flow_h": 45.0,
                    "flow_c": 50.0,
                    "cp_h": 2100.0,
                    "cp_c": 2000.0,
                    "area": eq.parameters.get("area").value if "area" in eq.parameters else 120.0,
                }

        execution = model.execute(equipment_id, inputs, timestamp)

        h_after = hashlib.sha256(data_path.read_bytes()).hexdigest()
        if h_before != h_after:
            raise EquipmentSourceMutation("Source dataset mutated during equipment simulation execution!")

        return execution

    @staticmethod
    def create_replay_snapshot(execution: EquipmentExecution) -> EquipmentReplaySnapshot:
        return EquipmentReplaySnapshot(
            snapshot_id=f"snap-{execution.execution_id}",
            execution_id=execution.execution_id,
            timestamp=execution.provenance.timestamp, # type: ignore
            recorded_inputs=execution.input_state,
            recorded_outputs=execution.output_state,
            provenance=execution.provenance,
            result_hash=execution.result_hash,
        )
