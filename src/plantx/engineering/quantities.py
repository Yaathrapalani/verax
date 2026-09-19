"""Strongly typed EngineeringQuantity data model."""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance
from src.plantx.engineering.dimensions import DimensionCategory


class QuantityStatus(str, Enum):
    VALID = "VALID"
    UNIT_UNRESOLVED = "UNIT_UNRESOLVED"
    DIMENSION_MISMATCH = "DIMENSION_MISMATCH"
    INCONSISTENT = "INCONSISTENT"
    UNAVAILABLE = "UNAVAILABLE"


class EngineeringQuantity(BaseModel):
    """Strongly typed engineering quantity object containing value, units, dimension, and lineage."""
    quantity_id: str = Field(..., description="Unique quantity ID")
    name: str = Field(..., description="Engineering parameter name")
    original_value: Any = Field(None, description="Raw unparsed value")
    original_unit: str = Field("UNKNOWN", description="Raw unit string")
    normalized_value: Optional[float] = Field(None, description="SI normalized float value")
    normalized_unit: Optional[str] = Field(None, description="SI unit symbol")
    dimension: Optional[DimensionCategory] = Field(None, description="Dimensional classification")
    observed_at: Optional[float] = Field(None, description="Evaluation timestamp T")
    status: QuantityStatus = Field(QuantityStatus.VALID, description="Quantity validity status")
    truth_state: TruthState = Field(TruthState.OBSERVED, description="Stage 0 truth state")
    calculation_ref: Optional[str] = Field(None, description="Calculation definition ID if derived")
    assumptions: List[str] = Field(default_factory=list, description="Explicit assumptions applied")
    constraints_checked: List[str] = Field(default_factory=list, description="Validated constraints")
    provenance: Provenance = Field(..., description="Immutable provenance lineage")
