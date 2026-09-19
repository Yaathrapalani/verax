"""Abstract EquipmentModel Contract and Registry for Stage 14."""

from typing import Dict, Any, List, Optional
from src.plantx.process.schemas import EquipmentType
from src.plantx.equipment.schemas import EquipmentExecution, SolverStatus


class EquipmentModelContract:
    """Abstract Equipment Model Contract."""

    def __init__(self, model_id: str, equipment_type: EquipmentType, model_version: str = "1.0.0"):
        self.model_id = model_id
        self.equipment_type = equipment_type
        self.model_version = model_version
        self.model_status = "NUMERICALLY_BENCHMARKED"

    def execute(self, equipment_id: str, inputs: Dict[str, Any], timestamp: float) -> EquipmentExecution:
        raise NotImplementedError()


class EquipmentRegistry:
    """Global Equipment Model Registry."""

    def __init__(self):
        self._registry: Dict[str, EquipmentModelContract] = {}

    def register_model(self, model: EquipmentModelContract) -> None:
        self._registry[model.model_id] = model

    def get_model(self, model_id: str) -> Optional[EquipmentModelContract]:
        return self._registry.get(model_id)

    def list_models(self) -> List[str]:
        return list(self._registry.keys())
