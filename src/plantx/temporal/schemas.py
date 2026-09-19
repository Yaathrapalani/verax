"""Enums and schemas for Temporal Evidence Layer."""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from src.plantx.domain.provenance import Provenance


class MissingnessReason(str, Enum):
    NOT_OBSERVED = "NOT_OBSERVED"
    SENSOR_OFFLINE = "SENSOR_OFFLINE"
    COMMUNICATION_LOSS = "COMMUNICATION_LOSS"
    INVALID_VALUE = "INVALID_VALUE"
    PARSER_MISSING = "PARSER_MISSING"
    OUT_OF_RANGE = "OUT_OF_RANGE"
    UNKNOWN = "UNKNOWN"


class TemporalStatus(str, Enum):
    VALID = "VALID"
    INVALID_TIMESTAMP = "INVALID_TIMESTAMP"
    DUPLICATE_TIMESTAMP = "DUPLICATE_TIMESTAMP"
    OUT_OF_ORDER = "OUT_OF_ORDER"
    TEMPORAL_GAP = "TEMPORAL_GAP"
    FUTURE_LEAKAGE_ATTEMPT = "FUTURE_LEAKAGE_ATTEMPT"


class SamplingClassification(str, Enum):
    REGULAR = "REGULAR"
    IRREGULAR = "IRREGULAR"
    SPARSE = "SPARSE"
    BURSTY = "BURSTY"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    UNKNOWN = "UNKNOWN"


class FreshnessStatus(str, Enum):
    FRESH = "FRESH"
    STALE = "STALE"
    FRESHNESS_UNSPECIFIED = "FRESHNESS_UNSPECIFIED"


class OverallTemporalUsability(str, Enum):
    USABLE = "USABLE"
    CONDITIONALLY_USABLE = "CONDITIONALLY_USABLE"
    UNAVAILABLE = "UNAVAILABLE"


class TemporalObservation(BaseModel):
    """First-class temporal observation data contract."""
    observation_id: str = Field(..., description="Unique observation ID")
    source_id: str = Field(..., description="Source evidence ID")
    asset_id: str = Field(..., description="Target asset ID")
    measurement_id: str = Field(..., description="Target measurement ID")
    observed_at: float = Field(..., description="Timestamp of physical observation (Time_hr or epoch)")
    received_at: Optional[float] = Field(None, description="System intake timestamp")
    value: Optional[float] = Field(None, description="Extracted numerical value")
    original_value: Any = Field(None, description="Raw unparsed value")
    original_unit: Optional[str] = Field(None, description="Raw unit string")
    normalized_value: Optional[float] = Field(None, description="SI normalized value")
    normalized_unit: Optional[str] = Field(None, description="SI unit tag")
    sampling_interval: Optional[float] = Field(None, description="Delta t from preceding observation")
    delta_t_from_previous: Optional[float] = Field(None, description="Interval difference")
    observation_age: Optional[float] = Field(None, description="Age relative to target evaluation time T")
    missing_status: MissingnessReason = Field(MissingnessReason.NOT_OBSERVED, description="Reason for missingness")
    validity_status: str = Field("VALID", description="Observation validity state")
    temporal_status: TemporalStatus = Field(TemporalStatus.VALID, description="Timestamp integrity status")
    is_imputed: bool = Field(False, description="Flag indicating if value is imputed")
    imputation_method: Optional[str] = Field(None, description="Imputation algorithm name")
    imputation_window: Optional[str] = Field(None, description="Context window used for imputation")
    provenance: Provenance = Field(..., description="Immutable provenance lineage")
    transformation_version: str = Field("1.0.0", description="Transformation pipeline version")


class FreshnessPolicy(BaseModel):
    """Explicit freshness bounds policy."""
    max_acceptable_age_hours: Dict[str, float] = Field(default_factory=dict, description="Max age per measurement_id")


class ImputationPolicy(BaseModel):
    """Explicit imputation governance policy."""
    imputation_enabled: bool = Field(False, description="Master governance switch")
    permitted_methods: List[str] = Field(default_factory=list, description="List of explicitly allowed methods")
    max_consecutive_missing: int = Field(3, description="Maximum missing count allowed to impute")


class TemporalEvidenceState(BaseModel):
    """Overall deterministic Temporal Evidence State."""
    target_time: float = Field(..., description="Evaluation timestamp T")
    timestamp_integrity: str = Field("PASS", description="Timestamp integrity summary")
    completeness_fraction: float = Field(1.0, description="Observed to total ratio")
    freshness_summary: Dict[str, FreshnessStatus] = Field(default_factory=dict, description="Status per measurement channel")
    sampling_classification: SamplingClassification = Field(SamplingClassification.UNKNOWN, description="Sampling regime")
    alignment_quality: str = Field("EXACT", description="Causal alignment rating")
    history_depth_hours: float = Field(0.0, description="Available context history span")
    imputation_fraction: float = Field(0.0, description="Imputed observations ratio")
    usability: OverallTemporalUsability = Field(OverallTemporalUsability.USABLE, description="Overall temporal usability status")
    provenance: Provenance = Field(..., description="Aggregate temporal state provenance")
