"""Canonical Pydantic Schemas for Stage 13 Thermodynamic State + Benchmark Runtime."""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance


class CompositionBasis(str, Enum):
    MOLE_FRACTION = "MOLE_FRACTION"
    MASS_FRACTION = "MASS_FRACTION"
    VOLUME_FRACTION = "VOLUME_FRACTION"
    UNKNOWN = "UNKNOWN"


class PhaseState(str, Enum):
    LIQUID = "LIQUID"
    VAPOR = "VAPOR"
    TWO_PHASE = "TWO_PHASE"
    SUPERCRITICAL = "SUPERCRITICAL"
    SOLID = "SOLID"
    UNKNOWN = "UNKNOWN"
    UNAVAILABLE = "UNAVAILABLE"


class PropertyPackageType(str, Enum):
    IDEAL_GAS = "IDEAL_GAS"
    REAL_FLUID_EOS = "REAL_FLUID_EOS"
    PENG_ROBINSON = "PENG_ROBINSON"
    EXTERNAL_ENGINE = "EXTERNAL_ENGINE"
    UNSUPPORTED = "UNSUPPORTED"


class PropertyAvailability(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    INVALID = "INVALID"
    OUT_OF_RANGE = "OUT_OF_RANGE"


class BenchmarkDomain(str, Enum):
    THERMODYNAMIC_STATE = "THERMODYNAMIC_STATE"
    EOS = "EOS"
    PHASE = "PHASE"
    TRANSPORT = "TRANSPORT"
    ENERGY = "ENERGY"
    BALANCE = "BALANCE"
    PROCESS = "PROCESS"


class EngineeringValidationLabel(str, Enum):
    SOFTWARE_VERIFIED = "SOFTWARE_VERIFIED"
    NUMERICALLY_BENCHMARKED = "NUMERICALLY_BENCHMARKED"
    ENGINEERING_VALIDATED = "ENGINEERING_VALIDATED"
    PARTIALLY_VALIDATED = "PARTIALLY_VALIDATED"
    RESEARCH_PROTOTYPE = "RESEARCH_PROTOTYPE"
    UNVALIDATED = "UNVALIDATED"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"


class ComponentIdentity(BaseModel):
    component_id: str
    canonical_name: str
    formula: Optional[str] = None
    molecular_weight: Optional[float] = Field(None, description="Molecular weight in g/mol")
    aliases: List[str] = Field(default_factory=list)
    source: str = "IDENTIFIED_COMPOUND"
    provenance: Provenance
    status: str = "RESOLVED"


class ReferenceState(BaseModel):
    package: str = "DEFAULT"
    convention: str = "STP"
    reference_temperature: float = 298.15
    reference_pressure: float = 101325.0
    reference_enthalpy: float = 0.0
    reference_entropy: float = 0.0
    provenance: Provenance


class ThermodynamicInput(BaseModel):
    temperature: float = Field(..., description="Temperature in Kelvin (K)")
    pressure: float = Field(..., description="Pressure in Pascals (Pa)")
    composition: Dict[str, float] = Field(default_factory=dict, description="Component name to fraction mapping")
    composition_basis: CompositionBasis = CompositionBasis.UNKNOWN
    phase_hint: PhaseState = PhaseState.UNKNOWN
    property_package: PropertyPackageType = PropertyPackageType.IDEAL_GAS
    calculation_context: Dict[str, Any] = Field(default_factory=dict)
    provenance: Provenance


class ThermodynamicState(BaseModel):
    state_id: str
    temperature: float = Field(..., description="Temperature in K")
    pressure: float = Field(..., description="Pressure in Pa")
    composition: Dict[str, float] = Field(default_factory=dict)
    composition_basis: CompositionBasis = CompositionBasis.UNKNOWN
    phase: PhaseState = PhaseState.UNAVAILABLE
    density: Optional[float] = Field(None, description="Density in kg/m3")
    specific_volume: Optional[float] = Field(None, description="Specific volume in m3/kg")
    enthalpy: Optional[float] = Field(None, description="Specific enthalpy in J/kg")
    internal_energy: Optional[float] = Field(None, description="Specific internal energy in J/kg")
    entropy: Optional[float] = Field(None, description="Specific entropy in J/(kg*K)")
    heat_capacity_cp: Optional[float] = Field(None, description="Cp in J/(kg*K)")
    heat_capacity_cv: Optional[float] = Field(None, description="Cv in J/(kg*K)")
    viscosity: Optional[float] = Field(None, description="Dynamic viscosity in Pa*s")
    thermal_conductivity: Optional[float] = Field(None, description="Thermal conductivity in W/(m*K)")
    compressibility_factor: Optional[float] = Field(None, description="Compressibility factor Z")
    property_package: PropertyPackageType = PropertyPackageType.IDEAL_GAS
    calculation_method: str = "ANALYTICAL_IDEAL_GAS"
    reference_state: Optional[ReferenceState] = None
    truth_state: TruthState = TruthState.INFERRED
    applicability: str = "VALID"
    provenance: Provenance
    result_hash: str = ""


class BenchmarkCase(BaseModel):
    benchmark_id: str
    domain: BenchmarkDomain
    description: str
    inputs: Dict[str, Any]
    expected_outputs: Dict[str, Any]
    reference_source: str
    reference_engine: str = "ANALYTICAL_REFERENCE"
    reference_version: str = "1.0.0"
    tolerance: float = 0.01
    provenance: Provenance
    license: str = "PROPRIETARY_BENCHMARK_LOCKED"
    status: str = "LOCKED_TEST"


class BenchmarkMetrics(BaseModel):
    mae: float = 0.0
    rmse: float = 0.0
    max_relative_error: float = 0.0
    bias: float = 0.0
    valid_cases: int = 0
    failed_cases: int = 0
    unsupported_cases: int = 0


class BenchmarkResult(BaseModel):
    benchmark_id: str
    implementation: str
    version: str = "1.0.0"
    case_count: int = 0
    valid_count: int = 0
    failed_count: int = 0
    unsupported_count: int = 0
    metrics: BenchmarkMetrics
    tolerance: float = 0.01
    validation_label: EngineeringValidationLabel = EngineeringValidationLabel.NUMERICALLY_BENCHMARKED
    pass_status: bool = True
    provenance: Provenance
    result_hash: str = ""
