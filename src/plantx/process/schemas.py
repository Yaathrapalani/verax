"""Canonical Pydantic Schemas for Stage 11 Process Engineering Model & Computational Plant Graph."""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance


class EquipmentType(str, Enum):
    PUMP = "PUMP"
    COMPRESSOR = "COMPRESSOR"
    HEAT_EXCHANGER = "HEAT_EXCHANGER"
    VALVE = "VALVE"
    FURNACE = "FURNACE"
    REACTOR = "REACTOR"
    SEPARATOR = "SEPARATOR"
    DISTILLATION_COLUMN = "DISTILLATION_COLUMN"
    TANK = "TANK"
    MIXER = "MIXER"
    SPLITTER = "SPLITTER"
    FILTER = "FILTER"
    UTILITY_SOURCE = "UTILITY_SOURCE"
    UTILITY_SINK = "UTILITY_SINK"
    UNKNOWN = "UNKNOWN"


class StreamPhase(str, Enum):
    LIQUID = "LIQUID"
    VAPOR = "VAPOR"
    GAS = "GAS"
    TWO_PHASE = "TWO_PHASE"
    SOLID = "SOLID"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"
    UNAVAILABLE = "UNAVAILABLE"


class ConnectionType(str, Enum):
    PROCESS = "PROCESS"
    UTILITY = "UTILITY"
    RECYCLE = "RECYCLE"
    BYPASS = "BYPASS"
    CONTROL = "CONTROL"
    UNKNOWN = "UNKNOWN"


class EntityResolutionState(str, Enum):
    RESOLVED = "RESOLVED"
    CANDIDATE_MATCH = "CANDIDATE_MATCH"
    CONFLICT = "CONFLICT"
    UNRESOLVED = "UNRESOLVED"


class BoundaryType(str, Enum):
    FEED = "FEED"
    PRODUCT = "PRODUCT"
    UTILITY = "UTILITY"
    ENVIRONMENT = "ENVIRONMENT"
    INITIAL_STATE = "INITIAL_STATE"
    OPERATING_CONSTRAINT = "OPERATING_CONSTRAINT"
    UNKNOWN = "UNKNOWN"


class NodeKind(str, Enum):
    PLANT = "PLANT"
    PROCESS_UNIT = "PROCESS_UNIT"
    EQUIPMENT = "EQUIPMENT"
    STREAM = "STREAM"
    MEASUREMENT = "MEASUREMENT"
    BOUNDARY = "BOUNDARY"
    PARAMETER = "PARAMETER"


class EdgeRelation(str, Enum):
    CONTAINS = "CONTAINS"
    CONNECTS_TO = "CONNECTS_TO"
    FEEDS = "FEEDS"
    RECEIVES = "RECEIVES"
    MEASURED_BY = "MEASURED_BY"
    HAS_PARAMETER = "HAS_PARAMETER"
    HAS_BOUNDARY = "HAS_BOUNDARY"
    BELONGS_TO_UNIT = "BELONGS_TO_UNIT"
    RECYCLES_TO = "RECYCLES_TO"
    UTILITY_CONNECTS = "UTILITY_CONNECTS"
    DERIVED_FROM = "DERIVED_FROM"


class GeometryReference(BaseModel):
    geometry_id: str
    entity_id: str
    geometry_type: str = "3D_BOUNDING_BOX"
    asset_reference: str
    coordinate_reference: Dict[str, float] = Field(default_factory=dict)
    scale: Dict[str, float] = Field(default_factory=dict)
    source: str = "REPRESENTATIVE_CAD_TEMPLATE"
    truth_state: TruthState = TruthState.REPRESENTATIVE
    provenance: Provenance


class ComponentFraction(BaseModel):
    component_name: str
    value: float
    unit: str = "mass_fraction"
    truth_state: TruthState = TruthState.UNRESOLVED


class ProcessStream(BaseModel):
    stream_id: str
    name: str
    source_equipment_id: Optional[str] = None
    destination_equipment_id: Optional[str] = None
    phase: StreamPhase = StreamPhase.UNAVAILABLE
    temperature: Optional[float] = Field(None, description="Stream temperature in °C")
    pressure: Optional[float] = Field(None, description="Stream pressure in bar (UNAVAILABLE if missing)")
    mass_flow: Optional[float] = Field(None, description="Mass flow rate in kg/s")
    volumetric_flow: Optional[float] = Field(None, description="Volumetric flow in m3/h")
    composition: Dict[str, ComponentFraction] = Field(default_factory=dict)
    density: Optional[float] = None
    heat_capacity: Optional[float] = None
    enthalpy: Optional[float] = None
    viscosity: Optional[float] = None
    thermal_conductivity: Optional[float] = None
    delta_p: Optional[float] = Field(None, description="Pressure drop (UNAVAILABLE if missing)")
    state: str = "OPERATIONAL"
    provenance: Provenance
    truth_state: TruthState = TruthState.OBSERVED
    resolution_state: EntityResolutionState = EntityResolutionState.RESOLVED


class ProcessConnection(BaseModel):
    connection_id: str
    source: str
    destination: str
    stream_id: str
    connection_type: ConnectionType = ConnectionType.PROCESS
    provenance: Provenance
    truth_state: TruthState = TruthState.OBSERVED


class MeasurementBinding(BaseModel):
    binding_id: str
    measurement_id: str
    entity_id: str
    variable: str
    unit: str
    timestamp: float
    temporal_status: str = "VALID"
    source: str
    provenance: Provenance
    truth_state: TruthState = TruthState.OBSERVED


class BoundaryCondition(BaseModel):
    boundary_id: str
    boundary_type: BoundaryType = BoundaryType.UNKNOWN
    entity_id: str
    variable: str
    value: float
    unit: str
    timestamp: float
    source: str
    truth_state: TruthState = TruthState.OBSERVED
    provenance: Provenance


class OperatingState(BaseModel):
    timestamp: float
    temperature: Optional[float] = None
    pressure: Optional[float] = None
    flow: Optional[float] = None
    load: Optional[float] = None
    state_variables: Dict[str, Any] = Field(default_factory=dict)
    availability: str = "AVAILABLE"
    provenance: Provenance
    truth_state: TruthState = TruthState.OBSERVED


class ProcessParameter(BaseModel):
    parameter_id: str
    name: str
    value: Optional[float] = None
    unit: str = "UNKNOWN"
    dimension: str = "UNKNOWN"
    source: str
    truth_state: TruthState = TruthState.ASSUMED
    resolution_state: EntityResolutionState = EntityResolutionState.RESOLVED
    validation_status: str = "VALIDATED"
    provenance: Provenance


class EquipmentModel(BaseModel):
    equipment_id: str
    equipment_type: EquipmentType
    name: str
    unit_id: Optional[str] = None
    inlet_stream_ids: List[str] = Field(default_factory=list)
    outlet_stream_ids: List[str] = Field(default_factory=list)
    parameters: Dict[str, ProcessParameter] = Field(default_factory=dict)
    measurements: List[MeasurementBinding] = Field(default_factory=list)
    operating_state: Optional[OperatingState] = None
    geometry_reference: Optional[GeometryReference] = None
    provenance: Provenance
    truth_state: TruthState = TruthState.OBSERVED
    resolution_state: EntityResolutionState = EntityResolutionState.RESOLVED


class HeatExchangerModel(EquipmentModel):
    equipment_type: EquipmentType = EquipmentType.HEAT_EXCHANGER
    hot_inlet: Optional[str] = None
    hot_outlet: Optional[str] = None
    cold_inlet: Optional[str] = None
    cold_outlet: Optional[str] = None
    area: Optional[float] = Field(None, description="Heat transfer area in m2")
    tube_count: Optional[int] = Field(None, description="Tube count")
    tube_diameter: Optional[float] = Field(None, description="Tube diameter in m")
    tube_length: Optional[float] = Field(None, description="Tube length in m")
    material: Optional[str] = Field(None, description="Construction material")
    design_pressure: Optional[float] = Field(None, description="Design pressure")
    design_temperature: Optional[float] = Field(None, description="Design temperature")
    fouling_reference: Optional[Dict[str, Any]] = None


class ProcessUnit(BaseModel):
    unit_id: str
    name: str
    unit_type: str = "PROCESSING_UNIT"
    equipment_ids: List[str] = Field(default_factory=list)
    stream_ids: List[str] = Field(default_factory=list)
    connections: List[ProcessConnection] = Field(default_factory=list)
    operating_state: Optional[OperatingState] = None
    provenance: Provenance
    truth_state: TruthState = TruthState.OBSERVED
    resolution_state: EntityResolutionState = EntityResolutionState.RESOLVED


class GraphNode(BaseModel):
    node_id: str
    node_kind: NodeKind
    name: str
    truth_state: TruthState
    payload: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    edge_id: str
    source_id: str
    target_id: str
    relation: EdgeRelation
    truth_state: TruthState = TruthState.OBSERVED
    payload: Dict[str, Any] = Field(default_factory=dict)


class PlantModel(BaseModel):
    plant_id: str
    name: str
    description: str
    schema_version: str = "1.0.0"
    model_version: str = "1.0.0"
    units: Dict[str, ProcessUnit] = Field(default_factory=dict)
    equipment: Dict[str, EquipmentModel] = Field(default_factory=dict)
    streams: Dict[str, ProcessStream] = Field(default_factory=dict)
    connections: List[ProcessConnection] = Field(default_factory=list)
    measurements: List[MeasurementBinding] = Field(default_factory=list)
    boundaries: List[BoundaryCondition] = Field(default_factory=list)
    operating_state: Optional[OperatingState] = None
    parameters: Dict[str, ProcessParameter] = Field(default_factory=dict)
    provenance: Provenance
    truth_state: TruthState = TruthState.OBSERVED
    entity_resolution_state: EntityResolutionState = EntityResolutionState.RESOLVED
    graph_hash: str = ""
