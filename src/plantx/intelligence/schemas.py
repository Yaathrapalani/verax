"""Canonical FoulingState and FoulingPrognosis data models for Stage 6 Intelligence Core."""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance
from src.plantx.engineering.quantities import EngineeringQuantity


class ModelStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    BENCHMARKED = "BENCHMARKED"
    CHALLENGER = "CHALLENGER"
    PROMOTED = "PROMOTED"
    REJECTED = "REJECTED"


class ForecastStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    INVALID_INPUT = "INVALID_INPUT"
    UNAVAILABLE = "UNAVAILABLE"


class FoulingState(BaseModel):
    """Canonical fouling state representation for an asset at time T."""
    asset_id: str = Field(..., description="Target asset ID")
    timestamp: float = Field(..., description="Evaluation timestamp T (Time_hr)")
    current_rf_derived: Optional[float] = Field(None, description="Current derived fouling resistance (m2K/W)")
    recent_delta_rf: Optional[float] = Field(None, description="Difference in Rf over context window")
    recent_growth_rate: Optional[float] = Field(None, description="Observed rate of Rf change (m2K/W per hour)")
    historical_context_hours: float = Field(168.0, description="Context history window depth")
    status: str = Field("VALID", description="State validity status")
    truth_state: TruthState = Field(TruthState.INFERRED, description="Stage 0 truth state")
    provenance: Provenance = Field(..., description="State lineage provenance")


class FoulingPrognosis(BaseModel):
    """Canonical fouling prognosis result object."""
    prognosis_id: str = Field(..., description="Unique prognosis identifier")
    asset_id: str = Field(..., description="Target asset ID")
    timestamp: float = Field(..., description="Forecast origin timestamp T (Time_hr)")
    horizon_hours: int = Field(..., description="Operational forecast horizon (1h, 6h, 24h)")
    target_definition: str = Field("R_f_derived(t+h)", description="Target definition string")
    prediction: Optional[float] = Field(None, description="Predicted Rf_derived value at t + h")
    model_id: str = Field(..., description="Predictive model family ID")
    model_version: str = Field("1.0.0", description="Predictive model version")
    feature_version: str = Field("1.0.0", description="Feature extraction version")
    input_window_hours: int = Field(168, description="Historical feature context window")
    training_scope: str = Field("synthetic physics-based benchmark", description="Explicit training dataset scope")
    evaluation_scope: str = Field("Validation split t=44,800..54,399", description="Validation evaluation scope")
    status: ForecastStatus = Field(..., description="Forecast status")
    baseline_reference: Dict[str, Any] = Field(default_factory=dict, description="Persistence baseline reference comparison")
    uncertainty_status: str = Field("NOT_IMPLEMENTED", description="Explicit uncertainty boundary status")
    mechanism_claim: str = Field("NONE", description="Explicit mechanism overclaim prohibition tag")
    provenance: Provenance = Field(..., description="Prognosis lineage provenance")
