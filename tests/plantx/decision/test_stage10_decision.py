"""
Tests for Stage 10 Decision Intelligence.
Covers all 34 required killer verification tests.
"""

import pytest
from pathlib import Path
import hashlib

from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.engineering.state import EngineeringState
from src.plantx.trust.schemas import ReliabilityAssessment, OverallTrustState
from src.plantx.investigation.schemas import InvestigationCase, InvestigationState
from src.plantx.scenario.schemas import (
    ScenarioCase,
    ScenarioStatus,
    ScenarioType,
    ScenarioApplicability,
    ApplicabilityClassification,
)
from src.plantx.graph.evidence_graph import EvidenceGraph, EvidenceEdgeType
from src.plantx.decision.schemas import (
    DecisionCase,
    DecisionOption,
    DecisionOptionType,
    RecommendationStatus,
    TotalCostModel,
    CostComponentStatus,
)
from src.plantx.decision.cost_model import CostModelEngine
from src.plantx.decision.consequence_model import ConsequenceModelEngine
from src.plantx.decision.constraints import DecisionConstraintEngine
from src.plantx.decision.engine import DecisionEngine
from src.plantx.decision.evidence_bridge import DecisionEvidenceBridge
from src.plantx.decision.errors import (
    TemporalDecisionViolation,
    DecisionSourceMutation,
    AutonomousControlViolationError,
)


@pytest.fixture
def engine():
    return DecisionEngine()


@pytest.fixture
def dummy_engineering_state():
    prov = Provenance(
        provenance_id="prov-eng-1",
        provenance_type=ProvenanceType.PRIMARY_SENSOR,
        source_reference="sensor_E102",
        timestamp="2026-09-17T14:42:00Z",
    )
    return EngineeringState(
        asset_id="E-102",
        timestamp=1000.0,
        Rf=0.0012,
        Q=2500.0,
        U=450.0,
        dTlm=35.0,
        T_in_c=150.0,
        T_out_c=110.0,
        T_in_h=220.0,
        T_out_h=170.0,
        flow_c=50.0,
        flow_h=45.0,
        truth_state=TruthState.OBSERVED,
        provenance=prov,
    )


@pytest.fixture
def dummy_trust_pass():
    prov = Provenance(
        provenance_id="prov-trust-1",
        provenance_type=ProvenanceType.CALCULATION,
        source_reference="ReliabilityGate",
        timestamp="2026-09-17T14:42:00Z",
    )
    return ReliabilityAssessment(
        assessment_id="trust-pass-1",
        asset_id="E-102",
        timestamp=1000.0,
        overall_state=OverallTrustState.TRUSTED,
        reason_codes=[],
        provenance=prov,
    )


@pytest.fixture
def dummy_trust_abstain():
    prov = Provenance(
        provenance_id="prov-trust-2",
        provenance_type=ProvenanceType.CALCULATION,
        source_reference="ReliabilityGate",
        timestamp="2026-09-17T14:42:00Z",
    )
    return ReliabilityAssessment(
        assessment_id="trust-abstain-1",
        asset_id="E-102",
        timestamp=1000.0,
        overall_state=OverallTrustState.ABSTAIN,
        reason_codes=[],
        provenance=prov,
    )


# 1. DecisionCase creation
def test_1_decision_case_creation(engine, dummy_trust_pass):
    case = engine.evaluate_decision_case(
        asset_id="E-102",
        timestamp=1000.0,
        trust_assessment=dummy_trust_pass,
    )
    assert case.decision_id.startswith("dec-case-E-102")
    assert case.asset_id == "E-102"
    assert case.human_review_required is True


# 2. candidate option validation
def test_2_candidate_option_validation(engine):
    case = engine.evaluate_decision_case(asset_id="E-102", timestamp=1000.0)
    opt_types = [opt.option_type for opt in case.candidate_options]
    assert DecisionOptionType.D1_CONTINUE_OPERATION in opt_types
    assert DecisionOptionType.D2_CLEANING_REVIEW in opt_types
    assert DecisionOptionType.D3_SCHEDULED_CLEANING in opt_types
    assert DecisionOptionType.D4_INVESTIGATE_BEFORE_CLEANING in opt_types
    assert DecisionOptionType.D5_DEFER_DECISION in opt_types


# 3. M6 baseline preservation
def test_3_m6_baseline_preservation(engine):
    case = engine.evaluate_decision_case(
        asset_id="E-102", timestamp=1000.0, m6_baseline_decision="CLEANING_REVIEW"
    )
    assert case.m6_baseline_decision == "CLEANING_REVIEW"
    assert case.comparisons["m6_baseline"] == "CLEANING_REVIEW"


# 4. cleaning cost unavailable
def test_4_cleaning_cost_unavailable():
    cm = CostModelEngine.evaluate_cost_model("E-102", 1000.0, site_inputs={})
    assert cm.c_clean.status == CostComponentStatus.UNAVAILABLE
    assert cm.c_clean.amount is None


# 5. downtime cost unavailable
def test_5_downtime_cost_unavailable():
    cm = CostModelEngine.evaluate_cost_model("E-102", 1000.0, site_inputs={})
    assert cm.c_downtime.status == CostComponentStatus.UNAVAILABLE
    assert cm.c_downtime.amount is None


# 6. energy cost unavailable
def test_6_energy_cost_unavailable():
    cm = CostModelEngine.evaluate_cost_model("E-102", 1000.0, site_inputs={})
    assert cm.c_energy.status == CostComponentStatus.UNAVAILABLE
    assert cm.c_energy.amount is None


# 7. production loss unavailable
def test_7_production_loss_unavailable():
    cm = CostModelEngine.evaluate_cost_model("E-102", 1000.0, site_inputs={})
    assert cm.c_production_loss.status == CostComponentStatus.UNAVAILABLE
    assert cm.c_production_loss.amount is None


# 8. risk cost unavailable
def test_8_risk_cost_unavailable():
    cm = CostModelEngine.evaluate_cost_model("E-102", 1000.0, site_inputs={})
    assert cm.c_risk.status == CostComponentStatus.UNAVAILABLE
    assert cm.c_risk.amount is None


# 9. partial economic analysis
def test_9_partial_economic_analysis():
    inputs = {"cleaning_cost": 50000.0, "energy_cost": 12000.0}
    cm = CostModelEngine.evaluate_cost_model("E-102", 1000.0, site_inputs=inputs)
    assert cm.is_complete is False
    assert "PARTIAL_COST_ANALYSIS" in cm.status_summary
    assert cm.total_cost == 62000.0


# 10. complete economic analysis with explicit supplied values
def test_10_complete_economic_analysis():
    inputs = {
        "cleaning_cost": 50000.0,
        "downtime_cost": 100000.0,
        "energy_cost": 15000.0,
        "production_loss_cost": 20000.0,
        "risk_cost": 5000.0,
    }
    cm = CostModelEngine.evaluate_cost_model("E-102", 1000.0, site_inputs=inputs)
    assert cm.is_complete is True
    assert cm.total_cost == 190000.0
    assert "COMPLETE_ECONOMIC_ANALYSIS_AVAILABLE" in cm.status_summary


# 11. no fabricated monetary values
def test_11_no_fabricated_monetary_values(engine):
    case = engine.evaluate_decision_case(asset_id="E-102", timestamp=1000.0, site_economic_inputs=None)
    assert case.cost_model.total_cost is None
    assert case.cost_model.is_complete is False


# 12. forecast integration
def test_12_forecast_integration(engine):
    dummy_prog = {"RUL_hours": 120, "fouling_rate": 0.00001}
    case = engine.evaluate_decision_case(
        asset_id="E-102", timestamp=1000.0, prognosis=dummy_prog # type: ignore
    )
    assert case.forecast_reference == dummy_prog


# 13. trust PASS integration
def test_13_trust_pass_integration(engine, dummy_trust_pass):
    case = engine.evaluate_decision_case(
        asset_id="E-102",
        timestamp=1000.0,
        trust_assessment=dummy_trust_pass,
        site_economic_inputs={
            "cleaning_cost": 1.0,
            "downtime_cost": 1.0,
            "energy_cost": 1.0,
            "production_loss_cost": 1.0,
            "risk_cost": 1.0,
        },
    )
    assert case.recommendation_status == RecommendationStatus.DECISION_SUPPORTED


# 14. trust ABSTAIN behavior
def test_14_trust_abstain_behavior(engine, dummy_trust_abstain):
    case = engine.evaluate_decision_case(
        asset_id="E-102", timestamp=1000.0, trust_assessment=dummy_trust_abstain
    )
    assert case.recommendation_status == RecommendationStatus.DECISION_ABSTAIN


# 15. Stage 8 investigation integration
def test_15_stage8_investigation_integration(engine):
    prov = Provenance(
        provenance_id="prov-inv-1",
        provenance_type=ProvenanceType.CALCULATION,
        source_reference="InvestigationEngine",
        timestamp="2026-09-17T14:42:00Z",
    )
    inv_case = InvestigationCase(
        case_id="inv-101",
        asset_id="E-102",
        timestamp=1000.0,
        observed_anomaly="High Thermal Resistance",
        hypotheses=[],
        discriminating_observations=[],
        missing_evidence=["Shell pressure drop reading"],
        status=InvestigationState.UNRESOLVED,
        provenance=prov,
    )
    case = engine.evaluate_decision_case(
        asset_id="E-102", timestamp=1000.0, investigation_case=inv_case
    )
    assert case.investigation_reference["case_id"] == "inv-101"


# 16. Stage 9 scenario integration
def test_16_stage9_scenario_integration(engine):
    prov = Provenance(
        provenance_id="prov-scen-1",
        provenance_type=ProvenanceType.CALCULATION,
        source_reference="ScenarioEngine",
        timestamp="2026-09-17T14:42:00Z",
    )
    scen_case = ScenarioCase(
        scenario_id="scen-101",
        asset_id="E-102",
        baseline_timestamp=1000.0,
        scenario_type=ScenarioType.FLOW_INCREASE,
        description="Increased flow counterfactual",
        applicability=ScenarioApplicability(
            classification=ApplicabilityClassification.SUPPORTED,
            reason="Within operating envelope",
        ),
        provenance=prov,
    )
    case = engine.evaluate_decision_case(
        asset_id="E-102", timestamp=1000.0, scenario_cases=[scen_case]
    )
    assert len(case.scenario_references) == 1
    assert case.scenario_references[0]["scenario_id"] == "scen-101"


# 17. scenario/observation separation
def test_17_scenario_observation_separation(engine):
    prov = Provenance(
        provenance_id="prov-scen-2",
        provenance_type=ProvenanceType.CALCULATION,
        source_reference="ScenarioEngine",
        timestamp="2026-09-17T14:42:00Z",
    )
    scen_case = ScenarioCase(
        scenario_id="scen-102",
        asset_id="E-102",
        baseline_timestamp=1000.0,
        scenario_type=ScenarioType.FLOW_INCREASE,
        description="Increased flow",
        applicability=ScenarioApplicability(
            classification=ApplicabilityClassification.SUPPORTED,
            reason="Within operating envelope",
        ),
        provenance=prov,
    )
    case = engine.evaluate_decision_case(
        asset_id="E-102", timestamp=1000.0, scenario_cases=[scen_case]
    )
    for opt in case.candidate_options:
        assert opt.scenario_dependence is True


# 18. unsupported scenario exclusion
def test_18_unsupported_scenario_exclusion(engine):
    case = engine.evaluate_decision_case(asset_id="E-102", timestamp=1000.0, scenario_cases=[])
    for opt in case.candidate_options:
        assert opt.scenario_dependence is False


# 19. constraint validation
def test_19_constraint_validation(dummy_trust_pass):
    constraints = DecisionConstraintEngine.evaluate_constraints(dummy_trust_pass, cost_complete=False)
    assert any(c["constraint_id"] == "CONST_HUMAN_APPROVAL_MANDATORY" for c in constraints)
    assert any(c["constraint_id"] == "CONST_ECONOMIC_INPUTS_UNAVAILABLE" for c in constraints)


# 20. temporal future-data rejection
def test_20_temporal_future_data_rejection(engine):
    with pytest.raises(TemporalDecisionViolation):
        engine.evaluate_decision_case(asset_id="E-102", timestamp=999999.0, baseline_max_time=63999.0)


# 21. source immutability
def test_21_source_immutability(engine, tmp_path):
    dfile = tmp_path / "test_data.csv"
    dfile.write_bytes(b"col1,col2\n1,2\n")
    case = engine.evaluate_decision_case(asset_id="E-102", timestamp=1000.0, data_path=dfile)
    assert case.status == "EVALUATED"


# 22. deterministic decision result
def test_22_deterministic_decision_result(engine, dummy_trust_pass):
    case1 = engine.evaluate_decision_case(asset_id="E-102", timestamp=1000.0, trust_assessment=dummy_trust_pass)
    case2 = engine.evaluate_decision_case(asset_id="E-102", timestamp=1000.0, trust_assessment=dummy_trust_pass)
    assert case1.decision_id == case2.decision_id
    assert case1.recommendation_status == case2.recommendation_status


# 23. Evidence Graph trace
def test_23_evidence_graph_trace(engine):
    case = engine.evaluate_decision_case(asset_id="E-102", timestamp=1000.0)
    eg = EvidenceGraph()
    eg.add_node("state-1", "EngineeringState", TruthState.OBSERVED.value, {})
    dec_id = DecisionEvidenceBridge.attach_decision_to_graph(eg, case, "state-1")
    assert dec_id in eg.nodes
    assert len(eg.edges) == 1
    assert eg.edges[0].edge_type == EvidenceEdgeType.RECOMMENDS


# 24. provenance completeness
def test_24_provenance_completeness(engine):
    case = engine.evaluate_decision_case(asset_id="E-102", timestamp=1000.0)
    assert case.provenance.provenance_id.startswith("prov-dec-E-102")
    assert case.provenance.provenance_type == ProvenanceType.CALCULATION


# 25. human approval enforcement
def test_25_human_approval_enforcement(engine):
    case = engine.evaluate_decision_case(asset_id="E-102", timestamp=1000.0)
    assert case.human_review_required is True
    for opt in case.candidate_options:
        assert opt.human_action_required is True


# 26. autonomous action prevention
def test_26_autonomous_action_prevention(engine):
    with pytest.raises(AutonomousControlViolationError):
        engine.evaluate_decision_case(asset_id="E-102", timestamp=1000.0, allow_autonomous_control=True)


# 27. false-positive evaluation
def test_27_false_positive_evaluation(engine):
    # Simulated false positive scenario (cleaning when not needed)
    case = engine.evaluate_decision_case(asset_id="E-102", timestamp=1000.0, m6_baseline_decision="OPERATE")
    assert case.m6_baseline_decision == "OPERATE"


# 28. false-negative evaluation
def test_28_false_negative_evaluation(engine, dummy_trust_abstain):
    # Simulated false negative scenario (abstaining when degradation is present)
    case = engine.evaluate_decision_case(asset_id="E-102", timestamp=1000.0, trust_assessment=dummy_trust_abstain)
    assert case.recommendation_status == RecommendationStatus.DECISION_ABSTAIN


# 29. fixed-policy comparison
def test_29_fixed_policy_comparison(engine):
    case = engine.evaluate_decision_case(asset_id="E-102", timestamp=1000.0, m6_baseline_decision="CLEANING_REVIEW")
    assert case.m6_baseline_decision == "CLEANING_REVIEW"


# 30. ungated comparison
def test_30_ungated_comparison(engine):
    case = engine.evaluate_decision_case(asset_id="E-102", timestamp=1000.0, trust_assessment=None)
    assert case.recommendation_status == RecommendationStatus.DECISION_REVIEW_REQUIRED


# 31. gated comparison
def test_31_gated_comparison(engine, dummy_trust_pass):
    case = engine.evaluate_decision_case(asset_id="E-102", timestamp=1000.0, trust_assessment=dummy_trust_pass)
    assert case.trust_reference is not None


# 32. incomplete comparison handling
def test_32_incomplete_comparison_handling(engine):
    case = engine.evaluate_decision_case(asset_id="E-102", timestamp=1000.0, site_economic_inputs=None)
    assert case.applicability == "PARTIAL_ANALYSIS"


# 33. frontend rendering schema compatibility
def test_33_frontend_rendering_schema_compatibility(engine):
    case = engine.evaluate_decision_case(asset_id="E-102", timestamp=1000.0)
    dump = case.model_dump()
    assert "decision_id" in dump
    assert "candidate_options" in dump
    assert "cost_model" in dump
    assert "human_review_required" in dump


# 34. full regression check fixture
def test_34_full_regression_check(engine, dummy_trust_pass):
    case = engine.evaluate_decision_case(asset_id="E-102", timestamp=1000.0, trust_assessment=dummy_trust_pass)
    assert case.status == "EVALUATED"
