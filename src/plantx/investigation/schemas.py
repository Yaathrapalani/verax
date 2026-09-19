"""Canonical schemas for Stage 8 Investigation Intelligence."""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance


class InvestigationState(str, Enum):
    DETECTED = "DETECTED"
    CONTEXTUALIZED = "CONTEXTUALIZED"
    HYPOTHESES_GENERATED = "HYPOTHESES_GENERATED"
    EVIDENCE_ASSESSED = "EVIDENCE_ASSESSED"
    DISCRIMINATION_REQUIRED = "DISCRIMINATION_REQUIRED"
    INVESTIGATION_RECOMMENDED = "INVESTIGATION_RECOMMENDED"
    AWAITING_EVIDENCE = "AWAITING_EVIDENCE"
    REASSESSED = "REASSESSED"
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"


class HypothesisAssessmentStatus(str, Enum):
    SUPPORTED_BY_AVAILABLE_EVIDENCE = "SUPPORTED_BY_AVAILABLE_EVIDENCE"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
    UNRESOLVED = "UNRESOLVED"


class EvidenceReference(BaseModel):
    evidence_id: str
    description: str
    source_reference: str
    timestamp: float
    truth_state: TruthState = TruthState.OBSERVED
    provenance: Provenance


class DiscriminatingObservation(BaseModel):
    observation_id: str
    description: str
    target_hypotheses: List[str]
    expected_information_gain_basis: str = Field("HEURISTIC", description="Information gain basis")
    availability: str = Field("UNAVAILABLE", description="Availability status")
    priority: str = Field("HIGH", description="Observation priority")
    provenance: Provenance


class InvestigationRecommendation(BaseModel):
    recommendation_id: str
    observation: str
    reason: str
    target_hypotheses: List[str]
    required_data: List[str]
    availability: str = Field("UNAVAILABLE", description="Data availability status")
    priority: str = Field("HIGH", description="Recommendation priority")
    human_action_required: bool = Field(True, description="Human investigation mandatory")
    provenance: Provenance


class InvestigationHypothesis(BaseModel):
    hypothesis_id: str
    name: str
    description: str
    domain: str = "HEAT_EXCHANGER_FOULING"
    status: HypothesisAssessmentStatus = HypothesisAssessmentStatus.UNRESOLVED
    evidence_support_score: Optional[float] = Field(None, description="Explicit heuristic support score (0.0..1.0)")
    supporting_evidence: List[EvidenceReference] = Field(default_factory=list)
    contradicting_evidence: List[EvidenceReference] = Field(default_factory=list)
    missing_evidence: List[str] = Field(default_factory=list)
    discriminating_observations: List[DiscriminatingObservation] = Field(default_factory=list)
    assessment_basis: str = Field("Heuristic Evidence Matching", description="Assessment explanation")
    provenance: Provenance


class ScenarioExecutionError(Exception):
    """Raised when an attempt is made to execute Stage 9 scenario simulations from Stage 8."""
    pass


class InvestigationCase(BaseModel):
    case_id: str
    asset_id: str
    timestamp: float
    trigger: str = Field("OBSERVED_ANOMALY", description="Investigation trigger description")
    observed_anomaly: str
    engineering_context: Dict[str, Any] = Field(default_factory=dict)
    forecast_reference: Optional[Dict[str, Any]] = None
    trust_reference: Optional[Dict[str, Any]] = None
    hypotheses: List[InvestigationHypothesis] = Field(default_factory=list)
    conflicting_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    missing_evidence: List[str] = Field(default_factory=list)
    discriminating_observations: List[DiscriminatingObservation] = Field(default_factory=list)
    recommended_investigation: Optional[InvestigationRecommendation] = None
    status: InvestigationState = InvestigationState.DETECTED
    mechanism_claim: str = Field("NONE", description="Prohibition on unsupported chemical mechanism claims")
    provenance: Provenance
