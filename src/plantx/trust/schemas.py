"""Canonical schemas for Stage 7 Trust, Uncertainty & Selective Prediction."""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance


class OverallTrustState(str, Enum):
    TRUSTED = "TRUSTED"
    CONDITIONALLY_TRUSTED = "CONDITIONALLY_TRUSTED"
    ABSTAIN = "ABSTAIN"
    UNAVAILABLE = "UNAVAILABLE"


class TrustCheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"


class TrustReasonCode(str, Enum):
    DATA_INCOMPLETE = "DATA_INCOMPLETE"
    STALE_EVIDENCE = "STALE_EVIDENCE"
    SENSOR_INVALID = "SENSOR_INVALID"
    SENSOR_UNKNOWN = "SENSOR_UNKNOWN"
    PHYSICS_INCONSISTENT = "PHYSICS_INCONSISTENT"
    REGIME_UNSUPPORTED = "REGIME_UNSUPPORTED"
    UNCERTAINTY_EXCESSIVE = "UNCERTAINTY_EXCESSIVE"
    CALIBRATION_UNAVAILABLE = "CALIBRATION_UNAVAILABLE"
    FORECAST_UNAVAILABLE = "FORECAST_UNAVAILABLE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


REASON_CODE_PRECEDENCE: List[TrustReasonCode] = [
    TrustReasonCode.DATA_INCOMPLETE,
    TrustReasonCode.STALE_EVIDENCE,
    TrustReasonCode.SENSOR_INVALID,
    TrustReasonCode.SENSOR_UNKNOWN,
    TrustReasonCode.PHYSICS_INCONSISTENT,
    TrustReasonCode.REGIME_UNSUPPORTED,
    TrustReasonCode.UNCERTAINTY_EXCESSIVE,
    TrustReasonCode.CALIBRATION_UNAVAILABLE,
    TrustReasonCode.FORECAST_UNAVAILABLE,
    TrustReasonCode.INSUFFICIENT_EVIDENCE,
]


class PredictionInterval(BaseModel):
    lower_bound: float
    upper_bound: float
    nominal_level: float = 0.95
    method: str = "GaussianProcess"
    model_version: str = "1.0.0"
    calibration_status: str = "UNCALIBRATED"


class CalibrationReport(BaseModel):
    nominal_level: float = 0.95
    empirical_coverage: float
    coverage_error: float
    mean_interval_width: float
    sample_count: int
    calibration_status: str


class RiskCoveragePoint(BaseModel):
    threshold: float
    coverage: float
    risk_mae: float
    accepted_count: int
    total_count: int


class SafetyViolationError(Exception):
    """Raised when an attempt is made to execute autonomous process control without human approval."""
    pass


class ReliabilityAssessment(BaseModel):
    """Canonical Stage 7 Trust & Reliability Assessment object."""
    assessment_id: str = Field(..., description="Unique assessment ID")
    asset_id: str = Field(..., description="Target asset ID")
    timestamp: float = Field(..., description="Evaluation timestamp T")
    forecast_reference: Dict[str, Any] = Field(default_factory=dict, description="Stage 6 prognosis reference")
    data_status: TrustCheckStatus = Field(TrustCheckStatus.PASS, description="Data trust check status")
    sensor_status: TrustCheckStatus = Field(TrustCheckStatus.PASS, description="Sensor validity check status")
    physics_status: TrustCheckStatus = Field(TrustCheckStatus.PASS, description="Physical consistency status")
    regime_status: TrustCheckStatus = Field(TrustCheckStatus.SUPPORTED, description="Regime support status")
    uncertainty_status: str = Field("NOT_IMPLEMENTED", description="Uncertainty calculation status")
    calibration_status: str = Field("UNCALIBRATED", description="Calibration evaluation status")
    prediction_interval: Optional[PredictionInterval] = Field(None, description="Prediction interval if computed")
    overall_state: OverallTrustState = Field(..., description="Canonical Trust State: TRUSTED / ABSTAIN / etc.")
    decision_permission: bool = Field(False, description="Explicit permission to influence decision")
    fallback_policy: str = Field("FIXED_TIME_BASED_MAINTENANCE_POLICY", description="Active explicit fallback policy")
    reason_codes: List[TrustReasonCode] = Field(default_factory=list, description="Machine-readable reason codes")
    check_details: Dict[str, Any] = Field(default_factory=dict, description="Detailed check outputs")
    provenance: Provenance = Field(..., description="Assessment lineage provenance")
