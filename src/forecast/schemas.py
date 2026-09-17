"""
Typed Schemas for FOUL-X M3 Baseline Forecasting.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ForecastStatus(str, Enum):
    SUCCESS = "SUCCESS"
    UNAVAILABLE = "UNAVAILABLE"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    INVALID_CURRENT_STATE = "INVALID_CURRENT_STATE"


class ForecastResult(BaseModel):
    """
    Common conceptual forecast result interface.
    Used by Persistence, Trend, and Moving Average baselines.
    """
    exchanger_id: str = Field(..., description="Heat exchanger ID (E01, E02, E03, E04, E05)")
    timestamp: float = Field(..., description="Forecast origin timestamp t (Time_hr)")
    horizon_hours: int = Field(..., description="Forecast horizon h in hours (e.g. 1, 6, 24, 72, 168)")
    prediction: Optional[float] = Field(None, description="Predicted R_f_derived at t + h")
    target_definition: str = Field("R_f_derived(t+h)", description="Target definition string")
    input_window_start: float = Field(..., description="Start of historical context window t-W")
    input_window_end: float = Field(..., description="End of historical context window t (inclusive)")
    status: ForecastStatus = Field(..., description="Forecast generation status")
    unavailable_reasons: List[str] = Field(default_factory=list, description="Reasons for prediction unavailability")
    provenance: List[str] = Field(default_factory=list, description="Input variables used")
    method: str = Field(..., description="Forecasting method name (e.g. Persistence, RecentTrend, MovingAverage)")
    model_version: str = Field("1.0", description="Baseline model/calculation version")

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
