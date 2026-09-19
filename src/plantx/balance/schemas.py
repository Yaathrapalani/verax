"""Canonical Pydantic Schemas for Stage 12 Process Graph Solver & Mass / Energy Balance Engine."""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance


class BalanceScopeType(str, Enum):
    EQUIPMENT = "EQUIPMENT"
    PROCESS_UNIT = "PROCESS_UNIT"
    PLANT = "PLANT"


class BalanceStatus(str, Enum):
    BALANCED = "BALANCED"
    BALANCED_WITH_LIMITATIONS = "BALANCED_WITH_LIMITATIONS"
    IMBALANCE = "IMBALANCE"
    PARTIALLY_EVALUATED = "PARTIALLY_EVALUATED"
    UNAVAILABLE = "UNAVAILABLE"
    INCONSISTENT = "INCONSISTENT"
    ABSTAIN = "ABSTAIN"


class StreamClassification(str, Enum):
    INTERNAL = "INTERNAL"
    EXTERNAL_INPUT = "EXTERNAL_INPUT"
    EXTERNAL_OUTPUT = "EXTERNAL_OUTPUT"
    RECYCLE_INTERNAL = "RECYCLE_INTERNAL"


class DiagnosticSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DiagnosticType(str, Enum):
    MISSING_INPUT = "MISSING_INPUT"
    UNIT_MISMATCH = "UNIT_MISMATCH"
    DIMENSION_MISMATCH = "DIMENSION_MISMATCH"
    TIMESTAMP_MISMATCH = "TIMESTAMP_MISMATCH"
    MASS_IMBALANCE = "MASS_IMBALANCE"
    ENERGY_IMBALANCE = "ENERGY_IMBALANCE"
    MISSING_BOUNDARY = "MISSING_BOUNDARY"
    MISSING_STREAM = "MISSING_STREAM"
    COMPOSITION_UNAVAILABLE = "COMPOSITION_UNAVAILABLE"
    ENTHALPY_UNAVAILABLE = "ENTHALPY_UNAVAILABLE"
    STATE_REGIME_UNRESOLVED = "STATE_REGIME_UNRESOLVED"
    POSSIBLE_SENSOR_ISSUE = "POSSIBLE_SENSOR_ISSUE"
    POSSIBLE_TOPOLOGY_ISSUE = "POSSIBLE_TOPOLOGY_ISSUE"
    RECYCLE_PRESENT = "RECYCLE_PRESENT"
    RECYCLE_SOLVER_NOT_IMPLEMENTED = "RECYCLE_SOLVER_NOT_IMPLEMENTED"


class BalanceDiagnostic(BaseModel):
    diagnostic_id: str
    diagnostic_type: DiagnosticType
    severity: DiagnosticSeverity = DiagnosticSeverity.WARNING
    description: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    provenance: Provenance


class MassBalanceResult(BaseModel):
    total_in: Optional[float] = Field(None, description="Total mass inflow (kg/s)")
    total_out: Optional[float] = Field(None, description="Total mass outflow (kg/s)")
    accumulation: float = Field(0.0, description="Mass accumulation rate (kg/s)")
    residual: Optional[float] = Field(None, description="Mass residual: total_in - total_out - accumulation")
    relative_residual: Optional[float] = Field(None, description="Relative residual fraction")
    unit: str = "kg/s"
    tolerance: float = Field(0.01, description="Mass balance relative tolerance")
    status: BalanceStatus = BalanceStatus.UNAVAILABLE
    inputs: List[str] = Field(default_factory=list)
    provenance: Provenance


class ComponentBalanceResult(BaseModel):
    component_name: str
    basis: str = "mass_fraction"
    total_in: Optional[float] = None
    total_out: Optional[float] = None
    residual: Optional[float] = None
    status: BalanceStatus = BalanceStatus.UNAVAILABLE
    provenance: Provenance


class EnergyBoundaryTerm(BaseModel):
    term_name: str
    value: Optional[float] = Field(None, description="Heat or work rate value (kW)")
    unit: str = "kW"
    source: str = "UNAVAILABLE"
    truth_state: TruthState = TruthState.UNRESOLVED
    provenance: Provenance


class EnergyBalanceResult(BaseModel):
    total_enthalpy_in: Optional[float] = Field(None, description="Total stream enthalpy inflow (kW)")
    total_enthalpy_out: Optional[float] = Field(None, description="Total stream enthalpy outflow (kW)")
    heat_in: Optional[EnergyBoundaryTerm] = None
    heat_out: Optional[EnergyBoundaryTerm] = None
    work_in: Optional[EnergyBoundaryTerm] = None
    work_out: Optional[EnergyBoundaryTerm] = None
    accumulation: float = Field(0.0, description="Energy accumulation rate (kW)")
    residual: Optional[float] = Field(None, description="Energy residual")
    relative_residual: Optional[float] = None
    unit: str = "kW"
    tolerance: float = Field(0.02, description="Energy balance relative tolerance")
    status: BalanceStatus = BalanceStatus.UNAVAILABLE
    inputs: List[str] = Field(default_factory=list)
    provenance: Provenance


class BalanceCase(BaseModel):
    balance_id: str
    scope_type: BalanceScopeType
    scope_id: str
    timestamp: float
    boundary: Dict[str, Any] = Field(default_factory=dict)
    input_streams: List[str] = Field(default_factory=list)
    output_streams: List[str] = Field(default_factory=list)
    internal_streams: List[str] = Field(default_factory=list)
    mass_balance: MassBalanceResult
    component_balances: Dict[str, ComponentBalanceResult] = Field(default_factory=dict)
    energy_balance: EnergyBalanceResult
    diagnostics: List[BalanceDiagnostic] = Field(default_factory=list)
    reconciliation: Dict[str, Any] = Field(default_factory=dict)
    missing_inputs: List[str] = Field(default_factory=list)
    inconsistencies: List[str] = Field(default_factory=list)
    status: BalanceStatus = BalanceStatus.PARTIALLY_EVALUATED
    provenance: Provenance
    evidence_reference: Dict[str, Any] = Field(default_factory=dict)
    graph_hash: str = ""
    result_hash: str = ""
    human_review_required: bool = Field(True, description="Human engineering review mandatory")
