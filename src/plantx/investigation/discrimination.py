"""Discriminating observation finder and investigation recommendation generator."""

from typing import List, Dict, Any
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.investigation.schemas import (
    DiscriminatingObservation,
    InvestigationRecommendation,
    InvestigationHypothesis,
)


class DiscriminationEngine:
    """Identifies discriminating observations and generates human-actionable investigation recommendations."""

    @staticmethod
    def find_discriminating_observations(
        hypotheses: List[InvestigationHypothesis],
        asset_id: str,
        timestamp: float,
    ) -> List[DiscriminatingObservation]:
        prov = Provenance(
            provenance_id=f"prov-disc-{asset_id}-{int(timestamp)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="DiscriminationEngine",
            timestamp="2026-09-17T14:12:00Z",
            transformation_applied="Discriminating Observation Finding",
        )
        
        obs_list = []
        # Key discriminator: Delta P history helps discriminate flow/hydraulic vs thermal fouling
        obs_list.append(
            DiscriminatingObservation(
                observation_id=f"disc-dp-{asset_id}-{int(timestamp)}",
                description="Differential Pressure (ΔP) history across tube/shell sides",
                target_hypotheses=["FOULING_ACCUMULATION", "FLOW_OR_HYDRAULIC_EFFECT"],
                expected_information_gain_basis="HEURISTIC (Helps discriminate hydraulic restriction vs thermal boundary layer growth)",
                availability="UNAVAILABLE",
                priority="HIGH",
                provenance=prov,
            )
        )
        # Feed composition / API drift history
        obs_list.append(
            DiscriminatingObservation(
                observation_id=f"disc-feed-{asset_id}-{int(timestamp)}",
                description="Feed crude composition and TAN/API laboratory history",
                target_hypotheses=["FOULING_ACCUMULATION", "FEED_PROPERTY_SHIFT"],
                expected_information_gain_basis="HEURISTIC (Helps discriminate feed quality shift vs operational fouling)",
                availability="UNAVAILABLE",
                priority="MEDIUM",
                provenance=prov,
            )
        )
        return obs_list

    @staticmethod
    def generate_recommendation(
        discriminating_obs: List[DiscriminatingObservation],
        asset_id: str,
        timestamp: float,
    ) -> InvestigationRecommendation:
        prov = Provenance(
            provenance_id=f"prov-rec-{asset_id}-{int(timestamp)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="DiscriminationEngine",
            timestamp="2026-09-17T14:12:00Z",
            transformation_applied="Investigation Recommendation Generation",
        )
        top_obs = discriminating_obs[0] if discriminating_obs else None
        
        if top_obs:
            return InvestigationRecommendation(
                recommendation_id=f"rec-{asset_id}-{int(timestamp)}",
                observation=top_obs.description,
                reason="High expected information gain to discriminate competing hypotheses (Fouling Accumulation vs Flow/Hydraulic Effect).",
                target_hypotheses=top_obs.target_hypotheses,
                required_data=["delta_p_history", "sensor_calibration_logs"],
                availability="UNAVAILABLE",
                priority="HIGH",
                human_action_required=True,
                provenance=prov,
            )
        
        return InvestigationRecommendation(
            recommendation_id=f"rec-gen-{asset_id}-{int(timestamp)}",
            observation="Perform visual inspection and manual pressure check",
            reason="General investigation recommendation under insufficient telemetry",
            target_hypotheses=["FOULING_ACCUMULATION"],
            required_data=["manual_inspection_report"],
            availability="UNAVAILABLE",
            priority="MEDIUM",
            human_action_required=True,
            provenance=prov,
        )
