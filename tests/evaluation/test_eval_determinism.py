import pytest
from src.foulx.gate.evaluator import ReliabilityGateEvaluator
from src.foulx.decision.evaluator import DecisionEngineEvaluator
from src.foulx.evaluation.schemas import PolicyType, EvaluationCondition
from src.foulx.evaluation.evaluator import PolicyExperimentEvaluator
from tests.evaluation.test_eval_evaluator import create_mock_instance

def test_evaluation_determinism():
    """
    Verifies that running evaluation twice on identical inputs produces identical results.
    """
    gate_eval = ReliabilityGateEvaluator()
    dec_eval = DecisionEngineEvaluator()
    evaluator = PolicyExperimentEvaluator(gate_eval, dec_eval)

    inst = create_mock_instance()

    res1 = evaluator.evaluate_single_instance(
        raw_record=inst["raw_record"],
        required_fields=inst["required_fields"],
        tag=inst["tag"],
        shell_name=inst["shell_name"],
        canonical_state=inst["canonical_state"],
        forecast_results=inst["forecast_results"],
        feature_vector=inst["feature_vector"],
        actual_future_rf=inst["actual_future_rf"],
        condition=EvaluationCondition.SUPPORTED,
        policy=PolicyType.GATED,
    )

    res2 = evaluator.evaluate_single_instance(
        raw_record=inst["raw_record"],
        required_fields=inst["required_fields"],
        tag=inst["tag"],
        shell_name=inst["shell_name"],
        canonical_state=inst["canonical_state"],
        forecast_results=inst["forecast_results"],
        feature_vector=inst["feature_vector"],
        actual_future_rf=inst["actual_future_rf"],
        condition=EvaluationCondition.SUPPORTED,
        policy=PolicyType.GATED,
    )

    assert res1.predicted_action == res2.predicted_action
    assert res1.gate_status == res2.gate_status
    assert res1.outcome_class == res2.outcome_class
    assert res1.actual_future_rf == res2.actual_future_rf
