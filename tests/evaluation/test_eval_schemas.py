import pytest
from src.foulx.evaluation.schemas import (
    PolicyType,
    EvaluationCondition,
    OutcomeClass,
    PolicyEvaluationResult,
    PolicySummaryResult,
    EvaluationProvenance,
)
from src.foulx.gate.schemas import GateStatus
from src.foulx.decision.schemas import DecisionState

def test_evaluation_schemas_instantiation():
    res = PolicyEvaluationResult(
        evaluation_id="eval_101",
        timestamp=55000.0,
        exchanger_id="E01",
        condition=EvaluationCondition.SUPPORTED,
        policy=PolicyType.GATED,
        current_rf=7.5e-8,
        forecast_horizon=24,
        predicted_rf=1.2e-7,
        actual_future_rf=1.6e-7,
        threshold=1.5e-7,
        predicted_action=DecisionState.CLEANING_REVIEW,
        actual_outcome="HIGH_FOULING",
        gate_status=GateStatus.PASS,
        fallback_used=False,
        outcome_class=OutcomeClass.USEFUL_RECOMMENDATION,
        reason_codes=[],
    )
    assert res.policy == PolicyType.GATED
    assert res.condition == EvaluationCondition.SUPPORTED
    assert res.outcome_class == OutcomeClass.USEFUL_RECOMMENDATION
    assert res.provenance.no_economic_claims is True

def test_summary_result_schema():
    summary = PolicySummaryResult(
        condition=EvaluationCondition.SHIFTED,
        policy=PolicyType.GATED,
        evaluated_cases=100,
        useful_count=10,
        harmful_count=0,
        unnecessary_count=0,
        abstention_count=90,
        no_action_count=0,
        correct_abstention_count=90,
        coverage=0.10,
        risk=0.0,
        configuration_reference={"exchanger_id": "E01"},
    )
    assert summary.coverage == 0.10
    assert summary.abstention_count == 90
