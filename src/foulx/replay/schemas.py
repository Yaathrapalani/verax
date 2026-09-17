"""
Typed Pydantic Schemas for FOUL-X M9.0 Deterministic Replay Engine.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from src.physics.schemas import CanonicalExchangerState
from src.forecast.schemas import ForecastResult
from src.foulx.gate.schemas import ReliabilityResult, GateStatus
from src.foulx.decision.schemas import DecisionResult, DecisionState
from src.foulx.evaluation.schemas import EvaluationCondition
from src.foulx.replay.reason_codes import ReplayReasonCode


class ReplayMode(str, Enum):
    """Canonical scenario modes for Replay."""
    NORMAL = "NORMAL"
    SHIFTED = "SHIFTED"


class ReplayProvenance(BaseModel):
    """Provenance tracking for ReplaySnapshot."""
    replay_version: str = Field("1.0", description="Replay Engine version")
    m2_version: str = Field("1.0", description="M2 Physics State Estimator version")
    m4_version: str = Field("1.0", description="M4.0 Ridge Prognosis version")
    m5_version: str = Field("1.0", description="M5.0 Reliability Gate version")
    m6_version: str = Field("1.0", description="M6.0 Decision Engine version")
    m7_version: str = Field("1.0", description="M7.0 Policy Experiment version")
    dataset_checksum: str = Field("c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9", description="Dataset SHA-256 checksum")
    no_future_leakage: bool = Field(True, description="Strict temporal safety invariant: no future information used")


class ReplaySnapshot(BaseModel):
    """
    Canonical single source of truth snapshot emitted at historical timestamp t.
    Safety invariant: No future information available at t is exposed as current state.
    """
    timestamp: float = Field(..., description="Authoritative replay timestamp t (Time_hr)")
    exchanger_id: str = Field(..., description="Target exchanger ID (E01, E02, E03, E04, E05)")
    scenario_mode: ReplayMode = Field(..., description="Scenario mode: NORMAL or SHIFTED")
    raw_state_reference: Dict[str, Any] = Field(default_factory=dict, description="Raw record at t <= timestamp")
    physics_state: CanonicalExchangerState = Field(..., description="Authoritative M2 physics state at t")
    forecast_state: List[ForecastResult] = Field(default_factory=list, description="Authoritative M4 forecast results from information available at t")
    reliability_state: ReliabilityResult = Field(..., description="Authoritative M5 reliability gate result at t")
    decision_state: DecisionResult = Field(..., description="Authoritative M6 decision result at t")
    evidence_reference: Dict[str, Any] = Field(default_factory=dict, description="Evidence trace lineage reference")
    reason_codes: List[ReplayReasonCode] = Field(default_factory=list, description="Replay reason codes")
    provenance: ReplayProvenance = Field(default_factory=ReplayProvenance, description="Provenance metadata")

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ReplayManifest(BaseModel):
    """Manifest describing historical dataset and model bounds for Replay."""
    dataset_checksum: str = Field("c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9")
    min_timestamp: float = Field(0.0)
    max_timestamp: float = Field(63999.0)
    step_size_hours: float = Field(1.0)
    train_boundary: Dict[str, float] = Field(default_factory=lambda: {"start": 0.0, "end": 44799.0})
    val_boundary: Dict[str, float] = Field(default_factory=lambda: {"start": 44800.0, "end": 54399.0})
    test_boundary: Dict[str, float] = Field(default_factory=lambda: {"start": 54400.0, "end": 63999.0})
    m2_version: str = Field("1.0")
    m4_version: str = Field("1.0")
    m5_version: str = Field("1.0")
    m6_version: str = Field("1.0")
    m7_version: str = Field("1.0")
    replay_version: str = Field("1.0")

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
