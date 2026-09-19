"""Provenance models and types for PLANT-X."""

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ProvenanceType(str, Enum):
    """Supported source evidence types."""
    DOCUMENT = "DOCUMENT"
    HISTORIAN = "HISTORIAN"
    SENSOR = "SENSOR"
    OPERATOR = "OPERATOR"
    CALCULATION = "CALCULATION"
    MODEL = "MODEL"
    SIMULATION = "SIMULATION"
    MANUAL_MAPPING = "MANUAL_MAPPING"
    REPRESENTATIVE_TEMPLATE = "REPRESENTATIVE_TEMPLATE"


class Provenance(BaseModel):
    """Traceable provenance metadata for derived or observed engineering results."""
    provenance_id: str = Field(..., description="Unique identifier for provenance record")
    provenance_type: ProvenanceType = Field(..., description="Classification of evidence source")
    source_reference: str = Field(..., description="URI, table, sensor tag, or file reference")
    agent_id: Optional[str] = Field(None, description="System user, model ID, or calculation script")
    timestamp: str = Field(..., description="ISO 8601 timestamp of record creation or sensing")
    transformation_applied: Optional[str] = Field(None, description="Description of processing/computation step")
    upstream_provenance_ids: List[str] = Field(default_factory=list, description="IDs of direct parent evidence items")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context attributes")
