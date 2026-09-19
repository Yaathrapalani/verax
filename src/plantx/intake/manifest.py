"""Manifest models for evidence intake."""

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from src.plantx.domain.provenance import Provenance


class ManifestStatus(str, Enum):
    INGESTED = "INGESTED"
    PARSED = "PARSED"
    FAILED = "FAILED"
    UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"


class EvidenceManifest(BaseModel):
    """Immutable evidence manifest for every ingested file or document source."""
    source_id: str = Field(..., description="Unique source identifier")
    filename: str = Field(..., description="Original filename")
    source_type: str = Field(..., description="Classification: Telemetry, Engineering, Operational, Visual")
    format: str = Field(..., description="File extension / MIME format")
    size_bytes: int = Field(..., description="File size in bytes")
    checksum_sha256: str = Field(..., description="SHA-256 checksum of source evidence")
    ingested_at: str = Field(..., description="ISO 8601 timestamp of ingestion")
    parser_name: str = Field(..., description="Parser name utilized")
    parser_version: str = Field("1.0.0", description="Parser version")
    status: ManifestStatus = Field(..., description="Manifest parsing status")
    coverage: float = Field(0.0, description="Extraction coverage ratio (0.0 to 1.0)")
    training_eligible: bool = Field(False, description="Data governance invariant: false by default")
    provenance: Provenance = Field(..., description="Immutable provenance lineage")
    metadata: Dict[str, Any] = Field(default_factory=dict)
