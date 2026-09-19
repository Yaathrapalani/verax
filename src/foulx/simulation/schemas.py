"""
Typed Pydantic Schemas for FOUL-X Full Historical Fouling Simulation Layer.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from src.foulx.replay.schemas import ReplaySnapshot, ReplayMode
from src.foulx.decision.schemas import DecisionState
from src.foulx.gate.schemas import GateStatus


class SimulationScenarioId(str, Enum):
    """Canonical demo simulation scenarios."""
    FULL_END_TO_END = "FULL_END_TO_END"
    NORMAL_LIFECYCLE = "NORMAL_LIFECYCLE"
    CLEANING_REVIEW = "CLEANING_REVIEW"
    OOD_REGIME_SHIFT = "OOD_REGIME_SHIFT"


class SimulationEventType(str, Enum):
    """Event log entry types."""
    SYSTEM_INIT = "SYSTEM_INIT"
    EXCHANGER_MONITORING = "EXCHANGER_MONITORING"
    FOULING_PROGRESSION = "FOULING_PROGRESSION"
    FORECAST_UPDATED = "FORECAST_UPDATED"
    RELIABILITY_PASS = "RELIABILITY_PASS"
    RELIABILITY_ABSTAIN = "RELIABILITY_ABSTAIN"
    CLEANING_REVIEW_TRIGGERED = "CLEANING_REVIEW_TRIGGERED"
    SIMULATED_CLEANING_RESET = "SIMULATED_CLEANING_RESET"
    POST_CLEANING_RESUME = "POST_CLEANING_RESUME"
    REGIME_SHIFT_OOD = "REGIME_SHIFT_OOD"
    FIXED_POLICY_FALLBACK = "FIXED_POLICY_FALLBACK"


class SimulationEventLogEntry(BaseModel):
    """Single entry in deterministic simulation event stream."""
    sequence_id: int = Field(..., description="Sequential log entry ID")
    timestamp_hr: float = Field(..., description="Actual dataset timestamp Time_hr")
    event_type: SimulationEventType = Field(..., description="Canonical event classification")
    message: str = Field(..., description="Concise, engineering-grade description")
    gate_status: GateStatus = Field(..., description="Authoritative M5 gate status")
    decision: DecisionState = Field(..., description="Authoritative M6 decision state")
    is_simulated_event: bool = Field(False, description="True if event is a demo-only simulated reset (not observed dataset clean)")


class SimulationFrame(BaseModel):
    """Single frame emitted by simulation engine."""
    frame_index: int = Field(..., description="0-indexed simulation frame number")
    timestamp_hr: float = Field(..., description="Actual dataset timestamp Time_hr")
    exchanger_id: str = Field(..., description="Target exchanger ID (E01-E05)")
    scenario_id: SimulationScenarioId = Field(..., description="Active simulation scenario")
    replay_snapshot: ReplaySnapshot = Field(..., description="Underlying M9 ReplaySnapshot")
    is_simulated_cleaning_active: bool = Field(False, description="True if currently in post-simulated-cleaning phase")
    simulated_rf_offset: float = Field(0.0, description="Demo-only offset applied during simulated reset phase")
    event_logs: List[SimulationEventLogEntry] = Field(default_factory=list, description="Accumulated event log history")


class SimulationSummary(BaseModel):
    """Summary metadata for full simulation execution."""
    scenario_id: SimulationScenarioId = Field(...)
    total_frames: int = Field(...)
    start_timestamp_hr: float = Field(...)
    end_timestamp_hr: float = Field(...)
    cleaning_review_occurred: bool = Field(False)
    simulated_reset_applied: bool = Field(False)
    ood_abstention_occurred: bool = Field(False)
    dataset_checksum: str = Field("c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9")
