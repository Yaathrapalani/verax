import pytest
from src.foulx.decision.schemas import DecisionState
from src.foulx.gate.schemas import GateStatus
from src.foulx.evaluation.schemas import OutcomeClass, PolicyType, EvaluationCondition, PolicyEvaluationResult
from src.foulx.evaluation.metrics import classify_outcome, compute_summary_metrics

def test_classify_outcome_useful():
    outcome = classify_outcome(
        policy=PolicyType.UNGATED,
        predicted_action=DecisionState.CLEANING_REVIEW,
        fallback_action=None,
        actual_future_rf=1.8e-7,
        threshold=1.5e-7,
        gate_status=GateStatus.PASS,
    )
    assert outcome == OutcomeClass.USEFUL_RECOMMENDATION

def test_classify_outcome_harmful_false_positive():
    outcome = classify_outcome(
        policy=PolicyType.UNGATED,
        predicted_action=DecisionState.CLEANING_REVIEW,
        fallback_action=None,
        actual_future_rf=1.0e-7,
        threshold=1.5e-7,
        gate_status=GateStatus.PASS,
    )
    assert outcome == OutcomeClass.UNNECESSARY_ACTION

def test_classify_outcome_correct_abstention_fallback():
    outcome = classify_outcome(
        policy=PolicyType.GATED,
        predicted_action=DecisionState.ABSTAIN,
        fallback_action=DecisionState.OPERATE,
        actual_future_rf=1.0e-7,
        threshold=1.5e-7,
        gate_status=GateStatus.ABSTAIN,
    )
    assert outcome == OutcomeClass.CORRECT_ABSTENTION_FALLBACK

def test_compute_summary_metrics_coverage_risk():
    results = [
        PolicyEvaluationResult(
            evaluation_id="1", timestamp=55000.0, exchanger_id="E01",
            condition=EvaluationCondition.SUPPORTED, policy=PolicyType.GATED,
            current_rf=1.0e-7, forecast_horizon=24, predicted_rf=1.6e-7,
            actual_future_rf=1.7e-7, threshold=1.5e-7,
            predicted_action=DecisionState.CLEANING_REVIEW, actual_outcome="HIGH_FOULING",
            gate_status=GateStatus.PASS, fallback_used=False,
            outcome_class=OutcomeClass.USEFUL_RECOMMENDATION, reason_codes=[],
        ),
        PolicyEvaluationResult(
            evaluation_id="2", timestamp=55001.0, exchanger_id="E01",
            condition=EvaluationCondition.SUPPORTED, policy=PolicyType.GATED,
            current_rf=1.0e-7, forecast_horizon=24, predicted_rf=1.6e-7,
            actual_future_rf=1.0e-7, threshold=1.5e-7,
            predicted_action=DecisionState.ABSTAIN, actual_outcome="LOW_FOULING",
            gate_status=GateStatus.ABSTAIN, fallback_used=True,
            outcome_class=OutcomeClass.CORRECT_ABSTENTION_FALLBACK, reason_codes=[],
        ),
    ]

    summary = compute_summary_metrics(results, EvaluationCondition.SUPPORTED, PolicyType.GATED, {})
    assert summary.evaluated_cases == 2
    assert summary.coverage == 0.5 # 1 PASS out of 2 cases
    assert summary.risk == 0.0 # 0 harmful out of 1 non-abstained case
