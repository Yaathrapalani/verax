"""Applicability assessment engine for Stage 9 scenarios."""

from typing import Dict, Any, List, Optional
from src.plantx.scenario.schemas import (
    ScenarioType,
    ScenarioApplicability,
    ApplicabilityClassification,
)
from src.plantx.trust.schemas import ReliabilityAssessment, OverallTrustState


class ScenarioApplicabilityEngine:
    """Evaluates thermal vs hydraulic applicability classifications for scenario cases."""

    @staticmethod
    def evaluate_applicability(
        scenario_type: ScenarioType,
        trust_assessment: Optional[ReliabilityAssessment] = None,
        pressure_available: bool = False,
    ) -> ScenarioApplicability:
        assumptions = [
            "Prototype scenario bounds enforced",
            "No chemistry or reaction kinetics change assumed",
        ]
        
        # Hydraulic applicability is UNAVAILABLE in current synthetic benchmark dataset (no pressure/ΔP)
        hydraulic_status = ApplicabilityClassification.UNAVAILABLE
        if not pressure_available:
            assumptions.append("Hydraulic pressure/ΔP measurements unavailable in baseline dataset")

        if trust_assessment and trust_assessment.overall_state == OverallTrustState.ABSTAIN:
            return ScenarioApplicability(
                classification=ApplicabilityClassification.PARTIALLY_SUPPORTED,
                reason="Baseline state evaluated as ABSTAIN by Stage 7 Reliability Gate. Scenario proceeds with applicability downgrade.",
                thermal_support=ApplicabilityClassification.PARTIALLY_SUPPORTED,
                hydraulic_support=hydraulic_status,
                evidence_references=[trust_assessment.assessment_id],
                assumptions=assumptions,
            )

        return ScenarioApplicability(
            classification=ApplicabilityClassification.SUPPORTED,
            reason="Thermal calculations supported cleanly by Stage 5 Engineering Core. Hydraulic consequences remain unavailable.",
            thermal_support=ApplicabilityClassification.SUPPORTED,
            hydraulic_support=hydraulic_status,
            evidence_references=[],
            assumptions=assumptions,
        )
