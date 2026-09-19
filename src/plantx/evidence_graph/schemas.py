"""Typed schemas for Stage 4 Evidence Graph."""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance


class GraphNodeType(str, Enum):
    EVIDENCE_SOURCE = "EvidenceSource"
    EVIDENCE_RECORD = "EvidenceRecord"
    EXTRACTED_EVIDENCE = "ExtractedEvidence"
    CANONICAL_ENTITY = "CanonicalEntity"
    MEASUREMENT = "Measurement"
    TEMPORAL_OBSERVATION = "TemporalObservation"
    ENGINEERING_COMPUTATION = "EngineeringComputation"
    MODEL_EXECUTION = "ModelExecution"
    PREDICTION = "Prediction"
    UNCERTAINTY = "Uncertainty"
    HYPOTHESIS = "Hypothesis"
    INVESTIGATION = "Investigation"
    SCENARIO = "Scenario"
    DECISION = "Decision"
    HUMAN_APPROVAL = "HumanApproval"
    OUTCOME = "Outcome"
    ASSUMPTION = "Assumption"
    CONSTRAINT = "Constraint"


class GraphEdgeType(str, Enum):
    DERIVED_FROM = "DERIVED_FROM"
    EXTRACTED_FROM = "EXTRACTED_FROM"
    OBSERVED_IN = "OBSERVED_IN"
    MAPS_TO = "MAPS_TO"
    DESCRIBES = "DESCRIBES"
    MEASURES = "MEASURES"
    BELONGS_TO = "BELONGS_TO"
    DEPENDS_ON = "DEPENDS_ON"
    USES_INPUT = "USES_INPUT"
    USES_MODEL = "USES_MODEL"
    USES_VERSION = "USES_VERSION"
    USES_ASSUMPTION = "USES_ASSUMPTION"
    SUPPORTED_BY = "SUPPORTED_BY"
    CONSTRAINED_BY = "CONSTRAINED_BY"
    PRODUCES = "PRODUCES"
    PREDICTS = "PREDICTS"
    HAS_UNCERTAINTY = "HAS_UNCERTAINTY"
    CHALLENGES = "CHALLENGES"
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    INFLUENCES = "INFLUENCES"
    RESULTED_IN = "RESULTED_IN"
    APPROVED_BY = "APPROVED_BY"
    EVALUATED_BY = "EVALUATED_BY"
    FOLLOWED_BY = "FOLLOWED_BY"


class SufficiencyStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    UNRESOLVED = "UNRESOLVED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class EvidenceNodeV2(BaseModel):
    """Strongly typed graph node for Stage 4 Evidence Graph."""
    node_id: str = Field(..., description="Unique node ID")
    node_type: GraphNodeType = Field(..., description="Classification type of node")
    truth_state: TruthState = Field(..., description="Stage 0 truth state")
    observed_at: Optional[float] = Field(None, description="Observation or evaluation timestamp T")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Node attributes and payload")
    provenance: Provenance = Field(..., description="Immutable provenance lineage")


class EvidenceEdgeV2(BaseModel):
    """Strongly typed graph edge for Stage 4 Evidence Graph."""
    edge_id: str = Field(..., description="Unique edge ID")
    source_id: str = Field(..., description="Source node ID (upstream / origin)")
    target_id: str = Field(..., description="Target node ID (downstream / claim)")
    edge_type: GraphEdgeType = Field(..., description="Typed relationship classification")
    valid_at: Optional[float] = Field(None, description="Timestamp validity bound")
    provenance: Optional[Provenance] = Field(None, description="Edge lineage metadata")


class LineagePath(BaseModel):
    """Formal deterministic path representation for Forward / Backward traces."""
    root_node_id: str
    terminal_node_id: str
    nodes: List[EvidenceNodeV2] = Field(default_factory=list)
    edges: List[EvidenceEdgeV2] = Field(default_factory=list)
    path_status: SufficiencyStatus = Field(SufficiencyStatus.SUPPORTED)
    missing_evidence: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    temporal_constraints: List[str] = Field(default_factory=list)
    model_versions: List[str] = Field(default_factory=list)
    calculation_versions: List[str] = Field(default_factory=list)


class ClaimExplanation(BaseModel):
    """High-level API response for explain_claim(claim_id)."""
    claim_id: str
    status: SufficiencyStatus
    lineage: LineagePath
    supporting_evidence: List[str] = Field(default_factory=list)
    transformations: List[str] = Field(default_factory=list)
    models: List[str] = Field(default_factory=list)
    versions: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    uncertainty: Optional[Dict[str, Any]] = None
    temporal_scope: Optional[float] = None
    limitations: List[str] = Field(default_factory=list)


class ImpactAnalysis(BaseModel):
    """High-level API response for impact_analysis(node_id)."""
    node_id: str
    dependent_computations: List[str] = Field(default_factory=list)
    dependent_predictions: List[str] = Field(default_factory=list)
    dependent_decisions: List[str] = Field(default_factory=list)
    dependent_approvals: List[str] = Field(default_factory=list)
    dependent_outcomes: List[str] = Field(default_factory=list)
    downstream_paths: List[LineagePath] = Field(default_factory=list)
