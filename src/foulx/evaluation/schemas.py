"""
Typed Pydantic Schemas for FOUL-X M7.0 Policy Experiment.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from src.foulx.gate.schemas import GateStatus
from src.foulx.decision.schemas import DecisionState
from src.foulx.evaluation.reason_codes import EvaluationReasonCode


class PolicyType(str, Enum):
    """Canonical policy types for M7 experiment."""
    FIXED = "FIXED"
    UNGATED = "UNGATED"
    GATED = "GATED"


class EvaluationCondition(str, Enum):
    """Canonical evaluation conditions."""
    SUPPORTED = "SUPPORTED"
    SHIFTED = "SHIFTED"


class OutcomeClass(str, Enum):
    """
    Deterministic categorical outcome classes for policy decision evaluation.
    Evaluated against future observed ground truth Rf(t+h).
    """
    USEFUL_RECOMMENDATION = "USEFUL_RECOMMENDATION"
    HARMFUL_RECOMMENDATION = "HARMFUL_RECOMMENDATION"
    CORRECT_ABSTENTION_FALLBACK = "CORRECT_ABSTENTION_FALLBACK"
    UNNECESSARY_ACTION = "UNNECESSARY_ACTION"
    NO_ACTION = "NO_ACTION"


class EvaluationProvenance(BaseModel):
    """Provenance tracking for policy evaluation execution."""
    evaluation_version: str = Field("1.0", description="M7.0 Evaluation Engine version")
    m6_decision_version: str = Field("1.0", description="M6.0 Decision Engine version")
    m5_gate_version: str = Field("1.0", description="M5.0 Reliability Gate version")
    m4_model_version: str = Field("1.0", description="M4.0 Ridge Prognosis model version")
    dataset_checksum: str = Field("c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9", description="Dataset SHA-256 checksum")
    no_economic_claims: bool = Field(True, description="Explicit boundary: monetary/economic claims strictly forbidden")


class PolicyEvaluationResult(BaseModel):
    """
    Canonical result object for a single evaluation timestamp & policy.
    """
    evaluation_id: str = Field(..., description="Unique evaluation ID")
    timestamp: float = Field(..., description="Evaluation timestamp t (Time_hr)")
    exchanger_id: str = Field(..., description="Target exchanger ID")
    condition: EvaluationCondition = Field(..., description="Evaluation condition: SUPPORTED or SHIFTED")
    policy: PolicyType = Field(..., description="Policy type: FIXED, UNGATED, or GATED")
    current_rf: float = Field(..., description="Current observed Rf(t) derived proxy")
    forecast_horizon: int = Field(..., description="Forecast horizon h in hours (e.g. 24)")
    predicted_rf: Optional[float] = Field(None, description="Predicted Rf(t+h) from model (None for FIXED)")
    actual_future_rf: float = Field(..., description="Actual observed ground truth Rf(t+h) (evaluation-only)")
    threshold: float = Field(..., description="Configured fouling resistance decision threshold (m^2 K / W)")
    predicted_action: DecisionState = Field(..., description="Action produced by policy: OPERATE, CLEANING_REVIEW, or ABSTAIN")
    actual_outcome: str = Field(..., description="True state requirement: HIGH_FOULING or LOW_FOULING")
    gate_status: Optional[GateStatus] = Field(None, description="M5 gate status (None for FIXED/UNGATED)")
    fallback_used: bool = Field(False, description="True if GATED policy fell back to FIXED policy")
    outcome_class: OutcomeClass = Field(..., description="Categorical outcome classification")
    reason_codes: List[EvaluationReasonCode] = Field(default_factory=list, description="Evaluation reason codes")
    provenance: EvaluationProvenance = Field(default_factory=EvaluationProvenance, description="Provenance metadata")

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class PolicySummaryResult(BaseModel):
    """
    Summary metric object for a single policy under a specific condition.
    """
    condition: EvaluationCondition = Field(..., description="SUPPORTED or SHIFTED")
    policy: PolicyType = Field(..., description="FIXED, UNGATED, or GATED")
    evaluated_cases: int = Field(..., description="Total number of evaluated cases")
    useful_count: int = Field(..., description="Count of USEFUL_RECOMMENDATION outcomes")
    harmful_count: int = Field(..., description="Count of HARMFUL_RECOMMENDATION outcomes")
    unnecessary_count: int = Field(..., description="Count of UNNECESSARY_ACTION outcomes")
    abstention_count: int = Field(..., description="Count of gated ABSTAIN / fallback cases")
    no_action_count: int = Field(..., description="Count of NO_ACTION outcomes")
    correct_abstention_count: int = Field(..., description="Count of CORRECT_ABSTENTION_FALLBACK outcomes")
    coverage: float = Field(..., description="Coverage = non-abstained gated cases / eligible cases")
    risk: float = Field(..., description="Decision risk = harmful_count / non-abstained cases (or 0.0 if empty)")
    configuration_reference: Dict[str, Any] = Field(default_factory=dict, description="Configuration parameters reference")
    evaluation_version: str = Field("1.0", description="M7.0 Evaluation Engine version")

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
