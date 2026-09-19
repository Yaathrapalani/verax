"""Conservative entity resolution and conflict detection."""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ResolutionStatus(str, Enum):
    RESOLVED = "RESOLVED"
    CANDIDATE_MATCH = "CANDIDATE_MATCH"
    CONFLICT = "CONFLICT"
    UNRESOLVED = "UNRESOLVED"


class EntityResolutionResult(BaseModel):
    tag_evaluated: str
    canonical_id: Optional[str] = None
    status: ResolutionStatus
    evidence_sources: List[str] = Field(default_factory=list)
    conflict_details: Optional[str] = None


class ConservativeEntityResolver:
    """Conservative entity resolver preventing automatic merging of ambiguous tags."""

    # Explicit alias mapping dictionary requiring explicit engineering knowledge
    EXPLICIT_ALIASES = {
        "HX-101": "HX-101",
        "E-101": "HX-101",
        "E101": "HX-101",
    }

    @classmethod
    def resolve_asset_tag(cls, raw_tag: str, source_id: str, context_claims: List[Dict[str, Any]] = None) -> EntityResolutionResult:
        tag_clean = raw_tag.strip().upper()
        
        # Check for explicit conflict in context claims (e.g., P&ID vs Datasheet claiming different equipment types)
        if context_claims and len(context_claims) > 1:
            types = {c.get("equipment_type") for c in context_claims if c.get("equipment_type")}
            if len(types) > 1:
                return EntityResolutionResult(
                    tag_evaluated=raw_tag,
                    status=ResolutionStatus.CONFLICT,
                    evidence_sources=[c.get("source_id", "UNKNOWN") for c in context_claims],
                    conflict_details=f"Conflicting equipment types reported: {types}",
                )

        if tag_clean in cls.EXPLICIT_ALIASES:
            return EntityResolutionResult(
                tag_evaluated=raw_tag,
                canonical_id=cls.EXPLICIT_ALIASES[tag_clean],
                status=ResolutionStatus.RESOLVED,
                evidence_sources=[source_id],
            )

        # Conservative fallback: Do NOT guess unknown equipment tags
        return EntityResolutionResult(
            tag_evaluated=raw_tag,
            status=ResolutionStatus.UNRESOLVED,
            evidence_sources=[source_id],
        )
