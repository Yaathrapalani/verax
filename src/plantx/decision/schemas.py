"""Canonical schemas for Stage 10 Decision Intelligence."""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance


class DecisionOptionType(str, Enum):
    D1_CONTINUE_OPERATION = "D1_CONTINUE_OPERATION"
    D2_CLEANING_REVIEW = "D2_CLEANING_REVIEW"
    D3_SCHEDULED_CLEANING = "D3_SCHEDULED_CLEANING"
    D4_INVESTIGATE_BEFORE_CLEANING = "D4_INVESTIGATE_BEFORE_CLEANING"
    D5_DEFER_DECISION = "D5_DEFER_DECISION"


class RecommendationStatus(str, Enum):
    DECISION_SUPPORTED = "DECISION_SUPPORTED"
    DECISION_PARTIALLY_SUPPORTED = "DECISION_PARTIALLY_SUPPORTED"
    DECISION_UNAVAILABLE = "DECISION_UNAVAILABLE"
    DECISION_REVIEW_REQUIRED = "DECISION_REVIEW_REQUIRED"
    DECISION_ABSTAIN = "DECISION_ABSTAIN"


class CostComponentStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    PARTIAL = "PARTIAL"


class CostComponent(BaseModel):
    name: str
    amount: Optional[float] = None
    currency: str = "INR"
    unit: str = "CURRENCY"
    status: CostComponentStatus = CostComponentStatus.UNAVAILABLE
    source: str = "SITE_INPUT_REQUIRED"
    truth_state: TruthState = TruthState.UNRESOLVED
    assumption_status: str = "SITE_ECONOMIC_INPUTS_UNAVAILABLE"
    provenance: Provenance


class TotalCostModel(BaseModel):
    c_clean: CostComponent
    c_downtime: CostComponent
    c_energy: CostComponent
    c_production_loss: CostComponent
    c_risk: CostComponent
    total_cost: Optional[float] = None
    is_complete: bool = False
    status_summary: str = "ECONOMIC_ANALYSIS_UNAVAILABLE (Site economic inputs required)"


class ConsequenceItem(BaseModel):
    category: str
    description: str
    known_consequences: List[str] = Field(default_factory=list)
    unknown_consequences: List[str] = Field(default_factory=list)
    scenario_dependent: bool = False
    forecast_dependent: bool = True
    truth_state: TruthState = TruthState.INFERRED
    provenance: Provenance


class DecisionOption(BaseModel):
    option_id: str
    option_type: DecisionOptionType
    name: str
    description: str
    applicability: str = "SUPPORTED"
    known_costs: List[str] = Field(default_factory=list)
    unknown_costs: List[str] = Field(default_factory=list)
    consequences: ConsequenceItem
    evidence_basis: List[str] = Field(default_factory=list)
    scenario_dependence: bool = False
    forecast_dependence: bool = True
    trust_status: str = "PASS"
    constraint_status: str = "VALIDATED"
    human_action_required: bool = Field(True, description="Human engineering review mandatory")
    provenance: Provenance


class DecisionCase(BaseModel):
    decision_id: str
    asset_id: str
    timestamp: float
    m6_baseline_decision: str = "OPERATE"
    baseline_reference: Dict[str, Any] = Field(default_factory=dict)
    forecast_reference: Optional[Dict[str, Any]] = None
    trust_reference: Optional[Dict[str, Any]] = None
    investigation_reference: Optional[Dict[str, Any]] = None
    scenario_references: List[Dict[str, Any]] = Field(default_factory=list)
    candidate_options: List[DecisionOption] = Field(default_factory=list)
    cost_model: TotalCostModel
    constraints: List[Dict[str, Any]] = Field(default_factory=list)
    comparisons: Dict[str, Any] = Field(default_factory=dict)
    applicability: str = "PARTIAL_ANALYSIS"
    recommendation_status: RecommendationStatus = RecommendationStatus.DECISION_REVIEW_REQUIRED
    human_review_required: bool = Field(True, description="Human review unconditionally mandatory")
    provenance: Provenance
    status: str = "EVALUATED"
    disclaimer: str = Field(
        "Site-specific economic inputs (cleaning cost, downtime value, energy price, production valuation) are UNAVAILABLE in prototype dataset. Autonomous action is strictly prohibited.",
        description="Mandatory economic limitations disclaimer",
    )
