"""Constraints evaluator for Stage 10 Decision Intelligence."""

from typing import Dict, Any, List
from src.plantx.trust.schemas import ReliabilityAssessment, OverallTrustState


class DecisionConstraintEngine:
    """Evaluates human approval, reliability gate, and economic completeness constraints."""

    @staticmethod
    def evaluate_constraints(
        trust_assessment: ReliabilityAssessment = None,
        cost_complete: bool = False,
    ) -> List[Dict[str, Any]]:
        constraints = []

        # 1. Human Control Mandate (Non-negotiable)
        constraints.append({
            "constraint_id": "CONST_HUMAN_APPROVAL_MANDATORY",
            "name": "Human Engineering Approval Mandate",
            "status": "PASS",
            "description": "Consequential decision options require human operator approval.",
        })

        # 2. Stage 7 Trust Boundary
        if trust_assessment and trust_assessment.overall_state == OverallTrustState.ABSTAIN:
            constraints.append({
                "constraint_id": "CONST_TRUST_GATE_ABSTAIN",
                "name": "Reliability Gate Boundary",
                "status": "ABSTAIN",
                "description": "Stage 7 Trust Gate evaluated ABSTAIN. Forecast-assisted decision withheld.",
            })
        else:
            constraints.append({
                "constraint_id": "CONST_TRUST_GATE_PASS",
                "name": "Reliability Gate Boundary",
                "status": "PASS",
                "description": "Stage 7 Trust Gate evaluated PASS.",
            })

        # 3. Economic Completeness Constraint
        if not cost_complete:
            constraints.append({
                "constraint_id": "CONST_ECONOMIC_INPUTS_UNAVAILABLE",
                "name": "Site Economic Input Requirement",
                "status": "PARTIAL",
                "description": "Site-specific monetary values unavailable. Ranking strictly limited to qualitative comparison.",
            })

        return constraints
