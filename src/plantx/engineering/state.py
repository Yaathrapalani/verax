"""Canonical EngineeringState schema for Stage 5."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from src.plantx.domain.provenance import Provenance
from src.plantx.engineering.quantities import EngineeringQuantity


class EngineeringState(BaseModel):
    """Canonical engineering state of an asset at evaluation timestamp T."""
    asset_id: str = Field(..., description="Target asset ID")
    timestamp: float = Field(..., description="Evaluation timestamp T (Time_hr)")
    quantities: Dict[str, EngineeringQuantity] = Field(default_factory=dict, description="Calculated quantities")
    calculations_executed: List[str] = Field(default_factory=list, description="IDs of executed calculations")
    validity: str = Field("VALID", description="COMPUTABLE, VALID, CONDITIONALLY_VALID, INCONSISTENT, UNAVAILABLE")
    assumptions: List[str] = Field(default_factory=list, description="Explicit assumptions active in state")
    unavailable_items: List[Dict[str, Any]] = Field(default_factory=list, description="Unavailable engineering quantities with reasons")
    provenance: Provenance = Field(..., description="State lineage provenance")
