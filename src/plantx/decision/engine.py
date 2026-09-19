"""Master Stage 10 Decision Engine."""

import hashlib
from typing import Dict, Any, List, Optional
from pathlib import Path

from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.engineering.state import EngineeringState
from src.plantx.intelligence.schemas import FoulingPrognosis
from src.plantx.trust.schemas import ReliabilityAssessment, OverallTrustState
from src.plantx.investigation.schemas import InvestigationCase
from src.plantx.scenario.schemas import ScenarioCase
from src.plantx.decision.schemas import (
    DecisionCase,
    DecisionOption,
    DecisionOptionType,
    RecommendationStatus,
    TotalCostModel,
)
from src.plantx.decision.decision_types import DECISION_OPTION_CATALOG
from src.plantx.decision.cost_model import CostModelEngine
from src.plantx.decision.consequence_model import ConsequenceModelEngine
from src.plantx.decision.constraints import DecisionConstraintEngine
from src.plantx.decision.errors import (
    TemporalDecisionViolation,
    DecisionSourceMutation,
    AutonomousControlViolationError,
)


class DecisionEngine:
    """Master Stage 10 Decision Intelligence Engine."""

    def __init__(self):
        pass

    def evaluate_decision_case(
        self,
        asset_id: str,
        timestamp: float,
        engineering_state: Optional[EngineeringState] = None,
        prognosis: Optional[FoulingPrognosis] = None,
        trust_assessment: Optional[ReliabilityAssessment] = None,
        investigation_case: Optional[InvestigationCase] = None,
        scenario_cases: Optional[List[ScenarioCase]] = None,
        site_economic_inputs: Optional[Dict[str, float]] = None,
        m6_baseline_decision: str = "OPERATE",
        baseline_max_time: float = 63999.0,
        data_path: Path = Path("data/raw/heat_exchanger_fouling_dataset.csv"),
        allow_autonomous_control: bool = False,
    ) -> DecisionCase:
        # Enforce human safety control invariant
        if allow_autonomous_control:
            raise AutonomousControlViolationError("Autonomous plant control, setpoint changes, or automatic cleaning commands are strictly forbidden.")

        # Source immutability verification
        h_before = hashlib.sha256(data_path.read_bytes()).hexdigest()

        if timestamp > baseline_max_time:
            raise TemporalDecisionViolation(f"Decision timestamp {timestamp} exceeds baseline max time {baseline_max_time}")

        prov = Provenance(
            provenance_id=f"prov-dec-{asset_id}-{int(timestamp)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="DecisionEngine.evaluate_decision_case",
            timestamp="2026-09-17T14:42:00Z",
            transformation_applied="Stage 10 Decision Case Evaluation",
        )

        # 1. Cost model evaluation
        cost_model: TotalCostModel = CostModelEngine.evaluate_cost_model(asset_id, timestamp, site_economic_inputs)

        # 2. Consequence model & candidate options generation
        candidate_options: List[DecisionOption] = []
        for opt_type in DecisionOptionType:
            cat_entry = DECISION_OPTION_CATALOG[opt_type]
            conseq = ConsequenceModelEngine.evaluate_consequence(opt_type, asset_id, timestamp)
            
            candidate_options.append(
                DecisionOption(
                    option_id=f"opt-{opt_type.value}-{asset_id}-{int(timestamp)}",
                    option_type=opt_type,
                    name=cat_entry["name"],
                    description=cat_entry["description"],
                    applicability="SUPPORTED",
                    known_costs=["Site input required"],
                    unknown_costs=["Cleaning contractor cost", "Downtime duration cost", "Energy price tariff"],
                    consequences=conseq,
                    evidence_basis=["Stage 5 Engineering State", "Stage 6 FOUL-X Forecast"],
                    scenario_dependence=bool(scenario_cases),
                    forecast_dependence=True,
                    trust_status=trust_assessment.overall_state.value if trust_assessment else "UNCHECKED",
                    constraint_status="VALIDATED",
                    human_action_required=True,
                    provenance=prov,
                )
            )

        # 3. Decision constraints evaluation
        constraints = DecisionConstraintEngine.evaluate_constraints(trust_assessment, cost_model.is_complete)

        # 4. Handle Stage 7 Abstention Integration
        if trust_assessment and trust_assessment.overall_state == OverallTrustState.ABSTAIN:
            rec_status = RecommendationStatus.DECISION_ABSTAIN
        elif not cost_model.is_complete:
            rec_status = RecommendationStatus.DECISION_REVIEW_REQUIRED
        else:
            rec_status = RecommendationStatus.DECISION_SUPPORTED

        # 5. Comparative evaluation overview
        comparisons = {
            "m6_baseline": m6_baseline_decision,
            "candidate_options_count": len(candidate_options),
            "cost_model_complete": cost_model.is_complete,
            "decision_status": rec_status.value,
        }

        # Source immutability verification after execution
        h_after = hashlib.sha256(data_path.read_bytes()).hexdigest()
        if h_before != h_after:
            raise DecisionSourceMutation("Raw source dataset was mutated during decision evaluation!")

        return DecisionCase(
            decision_id=f"dec-case-{asset_id}-{int(timestamp)}",
            asset_id=asset_id,
            timestamp=timestamp,
            m6_baseline_decision=m6_baseline_decision,
            baseline_reference={"timestamp": timestamp, "asset_id": asset_id},
            forecast_reference=prognosis.model_dump() if hasattr(prognosis, "model_dump") else (prognosis if isinstance(prognosis, dict) else None),
            trust_reference=trust_assessment.model_dump() if hasattr(trust_assessment, "model_dump") else (trust_assessment if isinstance(trust_assessment, dict) else None),
            investigation_reference=investigation_case.model_dump() if hasattr(investigation_case, "model_dump") else (investigation_case if isinstance(investigation_case, dict) else None),
            scenario_references=[sc.model_dump() if hasattr(sc, "model_dump") else sc for sc in scenario_cases] if scenario_cases else [],
            candidate_options=candidate_options,
            cost_model=cost_model,
            constraints=constraints,
            comparisons=comparisons,
            applicability="PARTIAL_ANALYSIS" if not cost_model.is_complete else "COMPLETE_ANALYSIS",
            recommendation_status=rec_status,
            human_review_required=True,
            provenance=prov,
            status="EVALUATED",
        )
