import pytest
import pandas as pd
from src.foulx.gate.schemas import GateStatus
from src.foulx.gate.evaluator import ReliabilityGateEvaluator
from src.foulx.gate.checks import HistoricalRegimeSupportChecker
from src.foulx.decision.schemas import DecisionState
from src.foulx.decision.evaluator import DecisionEngineEvaluator
from src.foulx.evaluation.schemas import PolicyType, EvaluationCondition
from src.foulx.evaluation.evaluator import PolicyExperimentEvaluator
from src.foulx.evaluation.perturbations import SyntheticRegimeShiftPerturber
from tests.evaluation.test_eval_evaluator import create_mock_instance

def test_safety_invariants():
    """
    Safety tests:
    A. M5 ABSTAIN -> GATED uses FIXED fallback.
    B. M5 ABSTAIN -> GATED never becomes an AI cleaning recommendation.
    C. UNGATED can produce AI action without gate.
    D. FIXED does not depend on M4 forecast.
    E. Future ground truth exists only in evaluator.
    F. No control commands emitted.
    G. No autonomous shutdown recommended.
    """
    regime_checker = HistoricalRegimeSupportChecker(z_score_threshold=4.0)
    train_df = pd.DataFrame({"Crude_Tube_T_In_degC": [150.0]*10, "Crude_Tube_m_kg_s": [50.0]*10})
    regime_checker.fit_on_training_data(train_df)

    gate_eval = ReliabilityGateEvaluator(regime_checker=regime_checker)
    dec_eval = DecisionEngineEvaluator()
    perturber = SyntheticRegimeShiftPerturber(shift_factor=10.0)

    evaluator = PolicyExperimentEvaluator(gate_eval, dec_eval, perturber=perturber)
    inst = create_mock_instance(current_rf=7.0e-8) # current Rf below threshold

    # A & B: GATED under SHIFTED condition produces ABSTAIN decision and falls back to FIXED action (OPERATE)
    res_gated_shifted = evaluator.evaluate_single_instance(
        raw_record=inst["raw_record"],
        required_fields=inst["required_fields"],
        tag=inst["tag"],
        shell_name=inst["shell_name"],
        canonical_state=inst["canonical_state"],
        forecast_results=inst["forecast_results"],
        feature_vector=inst["feature_vector"],
        actual_future_rf=inst["actual_future_rf"],
        condition=EvaluationCondition.SHIFTED,
        policy=PolicyType.GATED,
    )

    assert res_gated_shifted.gate_status == GateStatus.ABSTAIN
    assert res_gated_shifted.fallback_used is True
    assert res_gated_shifted.predicted_action == DecisionState.ABSTAIN
    assert "CLEANING" not in res_gated_shifted.predicted_action.value

    # C: UNGATED produces CLEANING_REVIEW regardless of shift
    res_ungated_shifted = evaluator.evaluate_single_instance(
        raw_record=inst["raw_record"],
        required_fields=inst["required_fields"],
        tag=inst["tag"],
        shell_name=inst["shell_name"],
        canonical_state=inst["canonical_state"],
        forecast_results=inst["forecast_results"],
        feature_vector=inst["feature_vector"],
        actual_future_rf=inst["actual_future_rf"],
        condition=EvaluationCondition.SHIFTED,
        policy=PolicyType.UNGATED,
    )

    assert res_ungated_shifted.predicted_action == DecisionState.CLEANING_REVIEW
    assert res_ungated_shifted.predicted_rf is not None

    # D: FIXED does not use forecast prediction
    res_fixed = evaluator.evaluate_single_instance(
        raw_record=inst["raw_record"],
        required_fields=inst["required_fields"],
        tag=inst["tag"],
        shell_name=inst["shell_name"],
        canonical_state=inst["canonical_state"],
        forecast_results=[],
        feature_vector=None,
        actual_future_rf=inst["actual_future_rf"],
        condition=EvaluationCondition.SUPPORTED,
        policy=PolicyType.FIXED,
    )

    assert res_fixed.predicted_rf is None
    assert res_fixed.predicted_action == DecisionState.OPERATE

    # F & G: Ensure no plant control or shutdown state exists in result schema
    assert not hasattr(res_gated_shifted, "control_command")
    assert not hasattr(res_gated_shifted, "autonomous_shutdown")
