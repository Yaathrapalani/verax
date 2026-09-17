"""
Typed Pydantic Schemas for FOUL-X M6.0 Decision Engine.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from src.foulx.decision.reason_codes import DecisionReasonCode
from src.foulx.gate.schemas import GateStatus


class DecisionState(str, Enum):
    """
    Canonical Decision States.
    OPERATE = Forecast remains below threshold within planning horizon AND reliability == PASS.
    CLEANING_REVIEW = Forecast reaches/exceeds threshold within planning horizon AND reliability == PASS.
    ABSTAIN = Reliability == ABSTAIN or required decision inputs are missing/invalid.
    """
    OPERATE = "OPERATE"
    CLEANING_REVIEW = "CLEANING_REVIEW"
    ABSTAIN = "ABSTAIN"


class DecisionProvenance(BaseModel):
    """Provenance tracking for Decision Engine execution."""
    decision_version: str = Field("1.0", description="Decision Engine version")
    gate_version: str = Field("1.0", description="M5.0 Reliability Gate version")
    m4_model_version: str = Field("1.0", description="M4.0 Ridge Prognosis model version")
    m2_schema_version: str = Field("1.0", description="M2 Physics State schema version")
    human_approval_required: bool = Field(True, description="Human approval invariant flag (ALWAYS True)")


class DecisionResult(BaseModel):
    """
    Canonical result object emitted by the FOUL-X M6.0 Decision Engine.
    SAFETY INVARIANT: decision is ABSTAIN whenever reliability_status == ABSTAIN.
    """
    timestamp: float = Field(..., description="Evaluation timestamp (Time_hr)")
    exchanger_id: str = Field(..., description="Target exchanger ID")
    decision: DecisionState = Field(..., description="Canonical decision: OPERATE, CLEANING_REVIEW, or ABSTAIN")
    reliability_status: GateStatus = Field(..., description="Authoritative M5 Reliability Gate status")
    current_rf_derived: Optional[float] = Field(None, description="Current derived fouling resistance proxy R_f_derived(t) (m^2 K / W)")
    forecast_horizon_hours: int = Field(..., description="Evaluated forecast horizon in hours")
    threshold_rf: float = Field(..., description="Configured decision threshold R_f (m^2 K / W)")
    threshold_crossing: bool = Field(False, description="True if forecast trajectory reaches/exceeds threshold")
    estimated_crossing_horizon_hours: Optional[int] = Field(None, description="Earliest supported forecast horizon at which crossing is detected")
    reason_codes: List[DecisionReasonCode] = Field(default_factory=list, description="List of applicable decision reason codes in deterministic order")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Detailed evidence bundle")
    provenance: DecisionProvenance = Field(default_factory=DecisionProvenance, description="Provenance metadata")

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
