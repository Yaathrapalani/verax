"""Deterministic candidate hypothesis catalog for heat exchanger investigation."""

from typing import List, Dict, Any
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.investigation.schemas import InvestigationHypothesis, HypothesisAssessmentStatus

# Candidate hypotheses definitions
CATALOG_HYPOTHESES: Dict[str, Dict[str, str]] = {
    "H1": {
        "name": "FOULING_ACCUMULATION",
        "description": "Gradual buildup of thermal fouling deposits on tube/shell heat transfer surfaces.",
    },
    "H2": {
        "name": "OPERATING_REGIME_CHANGE",
        "description": "Shift in operating throughput, stream temperatures, or flow regimes.",
    },
    "H3": {
        "name": "SENSOR_MEASUREMENT_ISSUE",
        "description": "Temperature or flow sensor drift, calibration error, or signal degradation.",
    },
    "H4": {
        "name": "FEED_PROPERTY_SHIFT",
        "description": "Variation in crude oil API gravity, TAN, or compositional properties.",
    },
    "H5": {
        "name": "FLOW_OR_HYDRAULIC_EFFECT",
        "description": "Hydraulic pressure drop, maldistribution, or tube flow restriction.",
    },
}


class HypothesisCatalog:
    """Provides deterministic candidate hypothesis templates for heat exchanger investigation cases."""

    @staticmethod
    def get_candidate_hypotheses(timestamp: float, asset_id: str) -> List[InvestigationHypothesis]:
        hypotheses = []
        for h_id, h_info in CATALOG_HYPOTHESES.items():
            prov = Provenance(
                provenance_id=f"prov-hyp-{h_id}-{asset_id}-{int(timestamp)}",
                provenance_type=ProvenanceType.MODEL,
                source_reference="HypothesisCatalog",
                timestamp="2026-09-17T14:12:00Z",
                transformation_applied="Candidate Hypothesis Catalog Instantiation",
            )
            hypotheses.append(
                InvestigationHypothesis(
                    hypothesis_id=f"{h_id}-{asset_id}-{int(timestamp)}",
                    name=h_info["name"],
                    description=h_info["description"],
                    domain="HEAT_EXCHANGER_FOULING",
                    status=HypothesisAssessmentStatus.UNRESOLVED,
                    provenance=prov,
                )
            )
        return hypotheses
