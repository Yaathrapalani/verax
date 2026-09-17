"""
Typed Configured Thresholds for FOUL-X M6.0 Decision Engine.
Thresholds are site/process-dependent decision parameters ($m^2 \\cdot K / W$).
"""

from typing import Dict
from pydantic import BaseModel, Field


class DecisionThresholdConfig(BaseModel):
    """
    Configured Decision Parameters for FOUL-X Decision Support.
    Values represent site-dependent, process-specific fouling resistance limits (m^2 K / W).
    """
    rf_threshold: float = Field(..., description="Fouling resistance decision threshold in m^2 K / W")
    planning_horizon_hours: int = Field(24, description="Configured decision planning horizon in hours (e.g. 24)")
    exchanger_id: str = Field("E01", description="Target exchanger ID")


# Default site-dependent decision parameters based on primary scale std (~1.05e-7 m^2 K / W)
DEFAULT_DECISION_THRESHOLDS: Dict[str, DecisionThresholdConfig] = {
    "E01": DecisionThresholdConfig(rf_threshold=1.5e-7, planning_horizon_hours=24, exchanger_id="E01"),
    "E02": DecisionThresholdConfig(rf_threshold=1.5e-7, planning_horizon_hours=24, exchanger_id="E02"),
    "E03": DecisionThresholdConfig(rf_threshold=1.5e-7, planning_horizon_hours=24, exchanger_id="E03"),
    "E04": DecisionThresholdConfig(rf_threshold=1.5e-7, planning_horizon_hours=24, exchanger_id="E04"),
    "E05": DecisionThresholdConfig(rf_threshold=1.5e-7, planning_horizon_hours=24, exchanger_id="E05"),
}
