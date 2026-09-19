"""Consequence model for Stage 10 Decision Intelligence."""

from typing import Dict, Any, List
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.decision.schemas import ConsequenceItem, DecisionOptionType
from src.plantx.decision.decision_types import DECISION_OPTION_CATALOG


class ConsequenceModelEngine:
    """Constructs qualitative consequence models for candidate decision options."""

    @staticmethod
    def evaluate_consequence(
        option_type: DecisionOptionType,
        asset_id: str,
        timestamp: float,
        scenario_dependent: bool = False,
    ) -> ConsequenceItem:
        prov = Provenance(
            provenance_id=f"prov-conseq-{option_type.value}-{asset_id}-{int(timestamp)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="ConsequenceModelEngine",
            timestamp="2026-09-17T14:42:00Z",
            transformation_applied="Stage 10 Decision Consequence Mapping",
        )

        cat_entry = DECISION_OPTION_CATALOG.get(option_type, {})
        known = cat_entry.get("known_consequences", [])
        unknown = cat_entry.get("unknown_consequences", [])

        return ConsequenceItem(
            category=option_type.value,
            description=cat_entry.get("description", "Candidate decision option consequence"),
            known_consequences=known,
            unknown_consequences=unknown,
            scenario_dependent=scenario_dependent,
            forecast_dependent=True,
            truth_state=TruthState.INFERRED,
            provenance=prov,
        )
