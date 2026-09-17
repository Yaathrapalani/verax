"""
Typed Pydantic Schemas for FOUL-X M11.0 Red-Team Failure-Safety Harness.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from src.foulx.gate.schemas import GateStatus, CheckResult
from src.foulx.gate.reason_codes import ReliabilityReasonCode
from src.foulx.decision.schemas import DecisionState
from src.foulx.redteam.reason_codes import RedTeamScenarioCode


class RedTeamScenarioResult(BaseModel):
    """Result of an individual Red-Team failure-safety scenario execution."""
    scenario_code: RedTeamScenarioCode = Field(..., description="Scenario code identifier")
    description: str = Field(..., description="Detailed description of injected failure/condition")
    expected_gate_status: GateStatus = Field(..., description="Expected M5 Gate Status (PASS or ABSTAIN)")
    actual_gate_status: GateStatus = Field(..., description="Actual M5 Gate Status")
    expected_decision: DecisionState = Field(..., description="Expected M6 Decision State")
    actual_decision: DecisionState = Field(..., description="Actual M6 Decision State")
    expected_reason_codes: List[ReliabilityReasonCode] = Field(default_factory=list, description="Expected M5 reason codes in deterministic order")
    actual_reason_codes: List[ReliabilityReasonCode] = Field(default_factory=list, description="Actual M5 reason codes")
    fallback_used: bool = Field(False, description="True if GATED policy fell back to FIXED policy")
    ai_action_withheld: bool = Field(True, description="Safety Invariant: AI action withheld on failure")
    checks: List[CheckResult] = Field(default_factory=list, description="Detailed gate check results")
    passed: bool = Field(..., description="True if actual output matches expected safety behavior")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Execution evidence bundle")


class RedTeamSummary(BaseModel):
    """Summary metrics of Red-Team failure-safety validation suite."""
    total_scenarios: int = Field(..., description="Total Red-Team scenarios executed")
    passed_scenarios: int = Field(..., description="Count of passed safety scenarios")
    failed_scenarios: int = Field(..., description="Count of failed safety scenarios")
    safety_invariants_held: bool = Field(..., description="True if 100% of safety invariants held")
    dataset_checksum_verified: bool = Field(..., description="True if raw dataset SHA-256 hash was preserved")
    artifact_integrity_verified: bool = Field(..., description="True if baseline M2-M10 artifacts remained unmodified")
    version: str = Field("1.0", description="M11.0 Red-Team version")


class RedTeamManifest(BaseModel):
    """Manifest for M11.0 Red-Team Failure-Safety Harness."""
    version: str = Field("1.0.0")
    dataset_checksum: str = Field("c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9")
    scenarios_evaluated: List[RedTeamScenarioCode] = Field(default_factory=list)
    m2_version: str = Field("1.0")
    m4_version: str = Field("1.0")
    m5_version: str = Field("1.0")
    m6_version: str = Field("1.0")
    m7_version: str = Field("1.0")
    m9_version: str = Field("1.0")
    m10_version: str = Field("1.0")
    m11_version: str = Field("1.0")
    no_scientific_changes: bool = Field(True)
