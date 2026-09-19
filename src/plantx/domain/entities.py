"""Domain entities for PLANT-X foundation."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance


class DomainEntity(BaseModel):
    """Base domain model ensuring truth state, provenance, and versioning across all objects."""
    truth_state: TruthState = Field(..., description="Epistemological truth state")
    provenance: Optional[Provenance] = Field(None, description="Traceable provenance lineage")
    timestamp: Optional[str] = Field(None, description="ISO 8601 timestamp")
    version: str = Field("1.0.0", description="Schema version identifier")


class Measurement(DomainEntity):
    measurement_id: str
    sensor_id: str
    stream_id: str
    parameter_name: str
    value: float
    unit: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Material(DomainEntity):
    material_id: str
    name: str
    composition: Dict[str, float] = Field(default_factory=dict)
    phase: str = "LIQUID"


class Stream(DomainEntity):
    stream_id: str
    name: str
    source_asset_id: Optional[str] = None
    target_asset_id: Optional[str] = None
    material_id: Optional[str] = None
    flow_rate_unit: str = "kg/s"


class Geometry(DomainEntity):
    geometry_id: str
    asset_id: str
    surface_area_m2: Optional[float] = None
    tube_count: Optional[int] = None
    tube_length_m: Optional[float] = None
    shell_diameter_m: Optional[float] = None


class Constraint(DomainEntity):
    constraint_id: str
    asset_id: str
    name: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    unit: str


class Asset(DomainEntity):
    asset_id: str
    plant_id: str
    name: str
    asset_type: str
    geometry_id: Optional[str] = None
    constraint_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Plant(DomainEntity):
    plant_id: str
    name: str
    location: str
    asset_ids: List[str] = Field(default_factory=list)
    stream_ids: List[str] = Field(default_factory=list)


class Event(DomainEntity):
    event_id: str
    asset_id: str
    event_type: str
    description: str


class MaintenanceEvent(Event):
    action_taken: str
    cost_usd: Optional[float] = None
    downtime_hours: Optional[float] = None


class Evidence(DomainEntity):
    evidence_id: str
    source_type: str
    description: str
    raw_payload: Dict[str, Any] = Field(default_factory=dict)


class Computation(DomainEntity):
    computation_id: str
    name: str
    algorithm: str
    input_measurement_ids: List[str] = Field(default_factory=list)
    output_values: Dict[str, float] = Field(default_factory=dict)


class Prediction(DomainEntity):
    prediction_id: str
    model_id: str
    asset_id: str
    target_parameter: str
    predicted_value: float
    horizon_hours: float


class Uncertainty(DomainEntity):
    uncertainty_id: str
    prediction_id: str
    lower_bound: float
    upper_bound: float
    confidence_level: float = 0.95
    method: str = "STD_DEV"


class Hypothesis(DomainEntity):
    hypothesis_id: str
    asset_id: str
    statement: str
    confidence_score: float


class Investigation(DomainEntity):
    investigation_id: str
    asset_id: str
    hypothesis_ids: List[str] = Field(default_factory=list)
    status: str = "OPEN"


class Scenario(DomainEntity):
    scenario_id: str
    name: str
    assumptions: Dict[str, Any] = Field(default_factory=dict)


class HumanApproval(BaseModel):
    approval_id: str
    approver_id: str
    approved: bool
    timestamp: str
    comments: Optional[str] = None


class Outcome(DomainEntity):
    outcome_id: str
    decision_id: str
    observed_cost_usd: float
    actual_downtime_hours: float


class Decision(DomainEntity):
    decision_id: str
    asset_id: str
    evidence_ids: List[str] = Field(default_factory=list)
    prediction_id: Optional[str] = None
    uncertainty_id: Optional[str] = None
    recommendation: str
    abstention: bool = False
    reason: str
    human_approval: Optional[HumanApproval] = None
    outcome: Optional[Outcome] = None


class ModelVersion(BaseModel):
    version_id: str
    git_commit_hash: str
    created_at: str


class ModelContract(DomainEntity):
    model_id: str
    model_version: ModelVersion
    training_data_reference: str
    feature_version: str
    training_window: str
    validation_window: str
    test_window: str
    applicability: List[str]
    limitations: List[str]


class SimulationContract(DomainEntity):
    simulation_id: str
    engine_name: str  # e.g., Aspen Plus, DWSIM, Native
    input_mapping: Dict[str, Any]
    validation_status: str
    assumptions: List[str]
