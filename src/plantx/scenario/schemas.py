"""Canonical Pydantic Schemas for Stage 9 Scenario / What-If Intelligence."""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance


class ScenarioType(str, Enum):
    FLOW_INCREASE = "FLOW_INCREASE"
    FLOW_DECREASE = "FLOW_DECREASE"
    FEED_PROPERTY_SHIFT = "FEED_PROPERTY_SHIFT"
    HEAT_TRANSFER_DEGRADATION = "HEAT_TRANSFER_DEGRADATION"
    FOULING_ACCELERATION = "FOULING_ACCELERATION"
    SENSOR_UNAVAILABLE = "SENSOR_UNAVAILABLE"
    COMBINED_OPERATING_SHIFT = "COMBINED_OPERATING_SHIFT"


class ApplicabilityClassification(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    UNAVAILABLE = "UNAVAILABLE"


class ScenarioStatus(str, Enum):
    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    EXECUTED = "EXECUTED"
    COMPARED = "COMPARED"
    FAILED = "FAILED"


class ScenarioParameter(BaseModel):
    parameter_id: str
    variable: str
    asset_id: str
    baseline_value: Optional[float] = None
    baseline_unit: str = "UNKNOWN"
    scenario_value: Optional[float] = None
    scenario_unit: str = "UNKNOWN"
    perturbation_type: str = Field("RELATIVE_PERCENT", description="RELATIVE_PERCENT, ABSOLUTE, ASSUMED_FRACTION")
    perturbation_magnitude: float
    source: str = "HYPOTHETICAL_USER_SCENARIO"
    truth_state: TruthState = TruthState.SIMULATED
    assumption_status: str = "PROTOTYPE_SCENARIO_BOUND"
    validation_status: str = "VALIDATED"
    provenance: Provenance


class ScenarioResult(BaseModel):
    result_id: str
    variable: str
    baseline_value: Optional[float] = None
    scenario_value: Optional[float] = None
    delta: Optional[float] = None
    relative_delta: Optional[float] = None
    unit: str = "UNKNOWN"
    truth_state: TruthState = TruthState.SIMULATED
    calculation_reference: str = "Stage 5 Engineering Core Recalculation"
    applicability: ApplicabilityClassification = ApplicabilityClassification.SUPPORTED
    provenance: Provenance


class ScenarioApplicability(BaseModel):
    classification: ApplicabilityClassification
    reason: str
    thermal_support: ApplicabilityClassification = ApplicabilityClassification.SUPPORTED
    hydraulic_support: ApplicabilityClassification = ApplicabilityClassification.UNAVAILABLE
    evidence_references: List[str] = Field(default_factory=list)
    validation_reference: str = "Stage 9 Applicability Engine"
    assumptions: List[str] = Field(default_factory=list)


class ScenarioCase(BaseModel):
    scenario_id: str
    asset_id: str
    created_at: str = "2026-09-17T14:32:00Z"
    baseline_timestamp: float
    scenario_type: ScenarioType
    description: str
    parameters: List[ScenarioParameter] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    constraints: List[Dict[str, Any]] = Field(default_factory=list)
    applicability: ScenarioApplicability
    propagation_path: List[str] = Field(default_factory=list)
    baseline_state: Dict[str, Any] = Field(default_factory=dict)
    scenario_state: Dict[str, Any] = Field(default_factory=dict)
    results: Dict[str, ScenarioResult] = Field(default_factory=dict)
    impact_summary: Dict[str, Any] = Field(default_factory=dict)
    uncertainty_reference: str = "NOT_STATISTICALLY_JUSTIFIED"
    evidence_reference: Dict[str, Any] = Field(default_factory=dict)
    provenance: Provenance
    human_review_required: bool = Field(True, description="Human review unconditionally mandatory")
    status: ScenarioStatus = ScenarioStatus.CREATED
    disclaimer: str = Field("Prototype scenario bound — not a site-specific operating limit.", description="Mandatory prototype boundary disclaimer")
