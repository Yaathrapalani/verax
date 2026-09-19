"""Canonical Pydantic Schemas for Stage 14 Equipment Simulation Runtime."""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance
from src.plantx.process.schemas import EquipmentType, StreamPhase


class PortDirection(str, Enum):
    INLET = "INLET"
    OUTLET = "OUTLET"
    ENERGY_IN = "ENERGY_IN"
    ENERGY_OUT = "ENERGY_OUT"
    UTILITY_IN = "UTILITY_IN"
    UTILITY_OUT = "UTILITY_OUT"


class FlowArrangement(str, Enum):
    COUNTER_CURRENT = "COUNTER_CURRENT"
    PARALLEL_FLOW = "PARALLEL_FLOW"
    UNKNOWN = "UNKNOWN"


class SolverStatus(str, Enum):
    CONVERGED = "CONVERGED"
    CONVERGED_WITH_WARNINGS = "CONVERGED_WITH_WARNINGS"
    FAILED = "FAILED"
    UNAVAILABLE = "UNAVAILABLE"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    INVALID_INPUT = "INVALID_INPUT"


class SimulationMode(str, Enum):
    MODE_A_FORWARD_CALCULATION = "MODE_A_FORWARD_CALCULATION"
    MODE_B_PERFORMANCE_EVALUATION = "MODE_B_PERFORMANCE_EVALUATION"
    MODE_C_SCENARIO = "MODE_C_SCENARIO"
    MODE_D_FOULX_INTEGRATION = "MODE_D_FOULX_INTEGRATION"


class EquipmentPort(BaseModel):
    port_id: str
    equipment_id: str
    stream_id: Optional[str] = None
    direction: PortDirection = PortDirection.INLET
    state: str = "OPERATIONAL"
    truth_state: TruthState = TruthState.OBSERVED
    provenance: Provenance


class EquipmentExecution(BaseModel):
    execution_id: str
    equipment_id: str
    model_id: str
    model_version: str = "1.0.0"
    input_state: Dict[str, Any] = Field(default_factory=dict)
    output_state: Dict[str, Any] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    assumptions: List[str] = Field(default_factory=list)
    solver_status: SolverStatus = SolverStatus.CONVERGED
    validation_status: str = "VALIDATED"
    applicability: str = "NUMERICALLY_BENCHMARKED"
    provenance: Provenance
    result_hash: str = ""
    truth_state: TruthState = TruthState.SIMULATED


class EquipmentReplaySnapshot(BaseModel):
    snapshot_id: str
    execution_id: str
    timestamp: Any
    recorded_inputs: Dict[str, Any]
    recorded_outputs: Dict[str, Any]
    provenance: Provenance
    result_hash: str
