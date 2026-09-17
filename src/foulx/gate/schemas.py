"""
Typed Pydantic Schemas for FOUL-X M5.0 Reliability Gate.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from src.foulx.gate.reason_codes import ReliabilityReasonCode


class GateStatus(str, Enum):
    """
    Reliability Gate status output.
    PASS = All mandatory checks passed cleanly.
    ABSTAIN = At least one mandatory check failed; forecast withheld from decision support.
    """
    PASS = "PASS"
    ABSTAIN = "ABSTAIN"


class CheckStatus(str, Enum):
    """Status of an individual gate check."""
    PASS = "PASS"
    FAIL = "FAIL"


class CheckResult(BaseModel):
    """Result of an individual reliability check."""
    check_name: str = Field(..., description="Name of the check (e.g. DATA_COMPLETENESS, SENSOR_INVALIDITY, PHYSICS_CONSISTENCY, REGIME_SUPPORT)")
    status: CheckStatus = Field(..., description="Check status: PASS or FAIL")
    reason_code: Optional[ReliabilityReasonCode] = Field(None, description="Reason code if status is FAIL")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Detailed auditable check metrics and evidence")


class ForecastReference(BaseModel):
    """Reference metadata for the prognosis forecast being evaluated by the gate."""
    exchanger_id: str = Field(..., description="Heat exchanger tag (E01, E02, E03, E04, E05)")
    timestamp: float = Field(..., description="Forecast origin timestamp t (Time_hr)")
    horizon_hours: int = Field(..., description="Forecast horizon h (e.g. 1, 6, 24)")
    prediction: Optional[float] = Field(None, description="Predicted R_f_derived at t + h")
    model_method: str = Field("RidgeRegression", description="Forecasting model method")


class GateProvenance(BaseModel):
    """Provenance tracking for the Reliability Gate execution."""
    gate_version: str = Field("1.0", description="Reliability Gate implementation version")
    m2_schema_version: str = Field("1.0", description="M2 Physics State schema version")
    m4_model_version: str = Field("1.0", description="M4.0 Ridge Prognosis model version")
    source_variables: List[str] = Field(default_factory=list, description="Input variables evaluated by the gate")
    dataset_checksum: str = Field("c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9", description="Dataset SHA-256 checksum")


class ReliabilityResult(BaseModel):
    """
    Canonical result object emitted by the FOUL-X M5.0 Reliability Gate.
    Safety invariant: status is PASS iff reason_codes is empty and all checks passed.
    """
    timestamp: float = Field(..., description="Evaluation timestamp (Time_hr)")
    exchanger_id: str = Field(..., description="Exchanger ID evaluated")
    status: GateStatus = Field(..., description="Canonical Gate Decision: PASS or ABSTAIN")
    checks: List[CheckResult] = Field(default_factory=list, description="List of individual check results")
    reason_codes: List[ReliabilityReasonCode] = Field(default_factory=list, description="List of applicable reason codes in deterministic order")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Summary evidence bundle")
    forecast_reference: ForecastReference = Field(..., description="Metadata reference to evaluated forecast")
    provenance: GateProvenance = Field(default_factory=GateProvenance, description="Provenance metadata")

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
