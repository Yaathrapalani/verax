"""Evidence assessment engine for Stage 8 hypotheses."""

from typing import List, Dict, Any, Tuple
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.domain.truth_state import TruthState
from src.plantx.investigation.schemas import (
    InvestigationHypothesis,
    HypothesisAssessmentStatus,
    EvidenceReference,
)


class EvidenceAssessmentEngine:
    """Evaluates supporting, contradicting, and missing evidence for candidate hypotheses."""

    @staticmethod
    def assess_hypothesis(
        hypothesis: InvestigationHypothesis,
        supporting: List[EvidenceReference],
        contradicting: List[EvidenceReference],
        missing: List[str],
        conflicts: List[Dict[str, Any]] = None,
    ) -> InvestigationHypothesis:
        conflicts = conflicts or []
        
        updated = hypothesis.model_copy()
        updated.supporting_evidence = supporting
        updated.contradicting_evidence = contradicting
        updated.missing_evidence = missing

        # Calculate heuristic support score (0.0 .. 1.0)
        sup_cnt = len(supporting)
        con_cnt = len(contradicting)

        if conflicts:
            updated.status = HypothesisAssessmentStatus.CONFLICTING_EVIDENCE
            updated.assessment_basis = "Conflicting evidence sources detected across measurements"
            updated.evidence_support_score = 0.5
        elif sup_cnt > 0 and con_cnt == 0:
            updated.status = HypothesisAssessmentStatus.PARTIALLY_SUPPORTED if missing else HypothesisAssessmentStatus.SUPPORTED_BY_AVAILABLE_EVIDENCE
            updated.assessment_basis = f"Supported by {sup_cnt} evidence item(s)"
            updated.evidence_support_score = 0.8 if missing else 1.0
        elif sup_cnt > 0 and con_cnt > 0:
            updated.status = HypothesisAssessmentStatus.PARTIALLY_SUPPORTED
            updated.assessment_basis = f"Partially supported ({sup_cnt} for, {con_cnt} against)"
            updated.evidence_support_score = float(sup_cnt / (sup_cnt + con_cnt))
        elif con_cnt > 0 and sup_cnt == 0:
            updated.status = HypothesisAssessmentStatus.CONTRADICTED
            updated.assessment_basis = f"Contradicted by {con_cnt} evidence item(s)"
            updated.evidence_support_score = 0.0
        else:
            updated.status = HypothesisAssessmentStatus.INSUFFICIENT_EVIDENCE
            updated.assessment_basis = "Insufficient evidence available for evaluation"
            updated.evidence_support_score = 0.0

        return updated
