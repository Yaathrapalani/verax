"""Typed Pydantic schemas for PLANT-X Stage 3 Digital Shadow."""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance
from src.plantx.domain.entities import Asset, Stream, Measurement, Geometry, Event
from src.plantx.intake.resolver import ResolutionStatus
from src.plantx.temporal.schemas import TemporalObservation, TemporalEvidenceState


class ShadowIssue(BaseModel):
    """Structured issue or unknown parameter flag in Digital Shadow."""
    issue_id: str = Field(..., description="Unique issue identifier")
    entity_id: str = Field(..., description="Affected entity ID")
    issue_type: str = Field(..., description="Classification: UNRESOLVED, STALE, CONFLICT, MISSING")
    description: str = Field(..., description="Detailed description")
    provenance: Provenance = Field(..., description="Issue lineage")


class ShadowProvenance(BaseModel):
    """Provenance tracking for Digital Shadow reconstruction."""
    shadow_version: str = Field("1.0.0", description="Digital Shadow version")
    reconstructed_at: str = Field(..., description="ISO 8601 timestamp of reconstruction execution")
    target_time: float = Field(..., description="Evaluation timestamp T (Time_hr)")
    evidence_source_ids: List[str] = Field(default_factory=list, description="Consumed Stage 1/2 evidence source IDs")
    deterministic_hash: str = Field(..., description="Deterministic hash of snapshot payload")


class MeasurementBinding(BaseModel):
    """Binding linking sensor measurement to asset shadow."""
    binding_id: str
    measurement_id: str
    parameter_name: str
    value: Optional[float]
    unit: str
    truth_state: TruthState
    freshness_status: str
    provenance: Provenance


class GeometryState(BaseModel):
    """Geometry projection for asset shadow."""
    geometry_id: str
    asset_id: str
    surface_area_m2: Optional[float]
    tube_count: Optional[int]
    shell_diameter_m: Optional[float]
    truth_state: TruthState = Field(TruthState.REPRESENTATIVE, description="Explicit geometry truth state")
    provenance: Provenance


class AssetState(BaseModel):
    """Reconstructed time-aware state of an asset at T."""
    asset_id: str
    canonical_name: str
    asset_type: str
    resolution_status: ResolutionStatus
    truth_state: TruthState
    process_role: str = "HEAT_EXCHANGER"
    connected_stream_ids: List[str] = Field(default_factory=list)
    measurement_bindings: List[MeasurementBinding] = Field(default_factory=list)
    geometry_state: Optional[GeometryState] = None
    events: List[Event] = Field(default_factory=list)
    physics_ref: Optional[Dict[str, Any]] = Field(None, description="FOUL-X M2 physics state reference")
    fouling_ref: Optional[Dict[str, Any]] = Field(None, description="FOUL-X M2 fouling state reference")
    forecast_ref: Optional[Dict[str, Any]] = Field(None, description="FOUL-X M4 forecast reference")
    reliability_ref: Optional[Dict[str, Any]] = Field(None, description="FOUL-X M5 reliability reference")
    decision_ref: Optional[Dict[str, Any]] = Field(None, description="FOUL-X M6 decision reference")
    issues: List[ShadowIssue] = Field(default_factory=list)
    provenance: Provenance


class TopologyRelation(BaseModel):
    """Typed process relationship edge in Digital Shadow."""
    relation_id: str
    source_id: str
    target_id: str
    relation_type: str  # CONNECTED_TO, FEEDS, RECEIVES, MEASURES, HAS_EVENT
    truth_state: TruthState
    provenance: Provenance


class DigitalShadowSnapshot(BaseModel):
    """Canonical machine-readable representation of plant state at time T."""
    snapshot_id: str
    plant_id: str
    target_time: float
    asset_shadows: Dict[str, AssetState] = Field(default_factory=dict)
    stream_shadows: Dict[str, Stream] = Field(default_factory=dict)
    topology: List[TopologyRelation] = Field(default_factory=list)
    temporal_state: TemporalEvidenceState
    issues: List[ShadowIssue] = Field(default_factory=list)
    provenance: ShadowProvenance
