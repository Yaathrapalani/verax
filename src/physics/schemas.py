"""
Typed Canonical Physics State Schemas for FOUL-X.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class StateValidity(str, Enum):
    """
    Validity status enum.
    NOTE: VALID means 'calculation passed implemented numerical/domain checks',
    it does NOT mean 'physical state proven correct.'
    """
    VALID = "VALID"
    INVALID_INPUT = "INVALID_INPUT"
    INVALID_LMTD = "INVALID_LMTD"
    ZERO_FLOW = "ZERO_FLOW"
    NEAR_ZERO_DT = "NEAR_ZERO_DT"
    NONFINITE = "NONFINITE"
    INSUFFICIENT_BASELINE = "INSUFFICIENT_BASELINE"


class ThermalState(BaseModel):
    q_tube: Optional[float] = Field(None, description="Heat absorbed by tube fluid (Watts, >= 0)")
    q_shell: Optional[float] = Field(None, description="Heat released by shell fluid (Watts, >= 0)")
    thermal_balance_error: Optional[float] = Field(None, description="Relative discrepancy |Q_tube - Q_shell| / max(Q_tube, Q_shell)")
    delta_t_1: Optional[float] = Field(None, description="Temperature difference at end 1: T_s_in - T_t_out (K)")
    delta_t_2: Optional[float] = Field(None, description="Temperature difference at end 2: T_s_out - T_t_in (K)")
    lmtd: Optional[float] = Field(None, description="Logarithmic Mean Temperature Difference (K)")
    ua: Optional[float] = Field(None, description="Overall thermal conductance Q_tube / LMTD (W/K)")
    ua_clean_reference: Optional[float] = Field(None, description="Exchanger-specific initial window UA reference (W/K)")


class FoulingState(BaseModel):
    rf_derived: Optional[float] = Field(None, description="Derived fouling-resistance proxy: (1/UA) - (1/UA_clean) (m^2 K / W equivalent)")
    rf_relative_to_reference: Optional[float] = Field(None, description="Relative ratio UA / UA_clean_reference")


class DataQualityState(BaseModel):
    valid_input_count: int = Field(..., description="Count of valid numerical input signals")
    invalid_input_count: int = Field(..., description="Count of nonfinite or out-of-domain input signals")
    primary_status: StateValidity = Field(..., description="Primary validity status flag")
    reasons: List[str] = Field(default_factory=list, description="List of all detected failure/warning reasons")


class AvailabilityState(BaseModel):
    pressure_available: bool = Field(False, description="Hydraulic pressure measurements available")
    delta_p_available: bool = Field(False, description="Differential pressure measurements available")
    cleaning_event_available: bool = Field(False, description="Explicit cleaning event/reset timestamps available")


class ProvenanceState(BaseModel):
    source_variables: List[str] = Field(default_factory=list, description="List of raw input columns consumed")
    state_schema_version: str = Field("1.0", description="Canonical state schema structure version")
    calculation_version: str = Field("1.0", description="Thermodynamic physics calculation engine version")


class CanonicalExchangerState(BaseModel):
    timestamp: float = Field(..., description="Simulation time in hours (Time_hr)")
    exchanger_id: str = Field(..., description="Heat exchanger identifier (E01, E02, E03, E04, E05)")
    thermal: ThermalState = Field(..., description="Calculated thermal & energy balance state")
    fouling: FoulingState = Field(..., description="Derived fouling resistance proxy state")
    data_quality: DataQualityState = Field(..., description="Data quality, primary status, and failure reasons")
    availability: AvailabilityState = Field(default_factory=AvailabilityState, description="Sensor & data channel availability flags")
    provenance: ProvenanceState = Field(default_factory=ProvenanceState, description="Audit provenance & versions")

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
