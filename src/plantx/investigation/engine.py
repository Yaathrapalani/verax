"""Master Investigation Engine for Stage 8."""

import hashlib
from typing import Dict, Any, List, Optional
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.engineering.state import EngineeringState
from src.plantx.intelligence.schemas import FoulingState, FoulingPrognosis
from src.plantx.trust.schemas import ReliabilityAssessment
from src.plantx.investigation.schemas import (
    InvestigationCase,
    InvestigationState,
    InvestigationHypothesis,
    EvidenceReference,
    HypothesisAssessmentStatus,
    ScenarioExecutionError,
)
from src.plantx.investigation.hypotheses import HypothesisCatalog
from src.plantx.investigation.evidence_assessment import EvidenceAssessmentEngine
from src.plantx.investigation.discrimination import DiscriminationEngine


class InvestigationEngine:
    """Master Stage 8 Investigation Engine generating evidence-driven InvestigationCases."""

    def __init__(self):
        pass

    def create_case(
        self,
        asset_id: str,
        timestamp: float,
        observed_anomaly: str,
        engineering_state: Optional[EngineeringState] = None,
        fouling_state: Optional[FoulingState] = None,
        prognosis: Optional[FoulingPrognosis] = None,
        trust_assessment: Optional[ReliabilityAssessment] = None,
        raw_record: Optional[Dict[str, Any]] = None,
        conflicting_sources: Optional[List[Dict[str, Any]]] = None,
        allow_scenario_execution: bool = False,
    ) -> InvestigationCase:
        # Check stage boundary invariant
        if allow_scenario_execution:
            raise ScenarioExecutionError("Scenario execution belongs strictly to Stage 9. Stage 8 must not execute scenario simulations.")

        prov = Provenance(
            provenance_id=f"prov-case-{asset_id}-{int(timestamp)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="InvestigationEngine.create_case",
            timestamp="2026-09-17T14:12:00Z",
            transformation_applied="Stage 8 Investigation Case Creation",
        )

        # 1. Instantiate candidate hypotheses catalog
        hypotheses = HypothesisCatalog.get_candidate_hypotheses(timestamp, asset_id)

        # 2. Extract evidence items from inputs
        supporting_h1: List[EvidenceReference] = []
        contradicting_h1: List[EvidenceReference] = []
        missing_evidence: List[str] = [
            "delta_p_history",
            "feed_composition_history",
            "sensor_calibration_record",
            "wall_temperature_profile",
        ]

        if fouling_state and fouling_state.current_rf_derived is not None:
            prov_ev = Provenance(
                provenance_id=f"prov-ev-rf-{asset_id}-{int(timestamp)}",
                provenance_type=ProvenanceType.CALCULATION,
                source_reference="FoulingState",
                timestamp="2026-09-17T14:12:00Z",
                transformation_applied="Rf evidence extraction",
            )
            supporting_h1.append(
                EvidenceReference(
                    evidence_id=f"ev-rf-{asset_id}-{int(timestamp)}",
                    description=f"Observed derived thermal fouling resistance Rf={fouling_state.current_rf_derived:.6f} m2K/W",
                    source_reference="FoulingState",
                    timestamp=timestamp,
                    truth_state=TruthState.INFERRED,
                    provenance=prov_ev,
                )
            )

        # 3. Assess each hypothesis
        assessed_hypotheses = []
        for hyp in hypotheses:
            if hyp.name == "FOULING_ACCUMULATION":
                assessed = EvidenceAssessmentEngine.assess_hypothesis(
                    hyp,
                    supporting=supporting_h1,
                    contradicting=contradicting_h1,
                    missing=missing_evidence,
                    conflicts=conflicting_sources,
                )
            else:
                assessed = EvidenceAssessmentEngine.assess_hypothesis(
                    hyp,
                    supporting=[],
                    contradicting=[],
                    missing=missing_evidence,
                    conflicts=conflicting_sources,
                )
            assessed_hypotheses.append(assessed)

        # 4. Find discriminating observations
        disc_obs = DiscriminationEngine.find_discriminating_observations(assessed_hypotheses, asset_id, timestamp)

        # 5. Generate recommendation
        rec = DiscriminationEngine.generate_recommendation(disc_obs, asset_id, timestamp)

        # 6. Determine case status
        case_status = InvestigationState.INVESTIGATION_RECOMMENDED

        return InvestigationCase(
            case_id=f"invest-case-{asset_id}-{int(timestamp)}",
            asset_id=asset_id,
            timestamp=timestamp,
            trigger="OBSERVED_ANOMALY",
            observed_anomaly=observed_anomaly,
            engineering_context={
                "engineering_state_validity": engineering_state.validity if engineering_state else "UNAVAILABLE",
                "fouling_state_status": fouling_state.status if fouling_state else "UNAVAILABLE",
            },
            forecast_reference=prognosis.model_dump() if prognosis else None,
            trust_reference=trust_assessment.model_dump() if trust_assessment else None,
            hypotheses=assessed_hypotheses,
            conflicting_evidence=conflicting_sources or [],
            missing_evidence=missing_evidence,
            discriminating_observations=disc_obs,
            recommended_investigation=rec,
            status=case_status,
            mechanism_claim="NONE",
            provenance=prov,
        )
