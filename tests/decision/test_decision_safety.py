import pytest
from src.forecast.schemas import ForecastResult, ForecastStatus
from src.foulx.gate.schemas import ReliabilityResult, GateStatus, ForecastReference, GateProvenance
from src.foulx.decision import (
    DecisionEngineEvaluator,
    DecisionState,
    DecisionReasonCode,
    DecisionThresholdConfig,
)
from tests.decision.test_decision_evaluator import create_mock_canonical_state, create_mock_reliability_result

def test_safety_m5_abstain_propagation():
    evaluator = DecisionEngineEvaluator()
    rel_res_abstain = create_mock_reliability_result(GateStatus.ABSTAIN)
    state = create_mock_canonical_state(rf_val=7.2e-8)
    forecasts = [
        ForecastResult(exchanger_id="E01", timestamp=45000.0, horizon_hours=24, prediction=2.5e-7, input_window_start=44976.0, input_window_end=45000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression"),
    ]

    res = evaluator.evaluate_decision(rel_res_abstain, state, forecasts)

    # SAFETY INVARIANT: M5 ABSTAIN MUST propagate to M6 ABSTAIN and CANNOT become CLEANING_REVIEW or OPERATE
    assert res.decision == DecisionState.ABSTAIN
    assert res.decision != DecisionState.CLEANING_REVIEW
    assert res.decision != DecisionState.OPERATE
    assert DecisionReasonCode.RELIABILITY_ABSTAIN in res.reason_codes

def test_safety_missing_or_invalid_inputs():
    evaluator = DecisionEngineEvaluator()
    rel_res_pass = create_mock_reliability_result(GateStatus.PASS)

    # Missing state
    res_no_state = evaluator.evaluate_decision(rel_res_pass, None, [])
    assert res_no_state.decision == DecisionState.ABSTAIN
    assert DecisionReasonCode.CURRENT_STATE_UNAVAILABLE in res_no_state.reason_codes

    # Invalid threshold
    invalid_cfg = DecisionThresholdConfig(rf_threshold=-1.0, planning_horizon_hours=24, exchanger_id="E01")
    state = create_mock_canonical_state()
    forecasts = [
        ForecastResult(exchanger_id="E01", timestamp=45000.0, horizon_hours=24, prediction=1.0e-7, input_window_start=44976.0, input_window_end=45000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression"),
    ]
    res_bad_thresh = evaluator.evaluate_decision(rel_res_pass, state, forecasts, threshold_config=invalid_cfg)
    assert res_bad_thresh.decision == DecisionState.ABSTAIN
    assert DecisionReasonCode.INVALID_THRESHOLD in res_bad_thresh.reason_codes

def test_safety_no_shutdown_or_control_commands():
    """Ensure no control or automatic shutdown fields exist in DecisionResult."""
    evaluator = DecisionEngineEvaluator()
    rel_res = create_mock_reliability_result(GateStatus.PASS)
    state = create_mock_canonical_state(rf_val=7.2e-8)
    forecasts = [
        ForecastResult(exchanger_id="E01", timestamp=45000.0, horizon_hours=24, prediction=2.5e-7, input_window_start=44976.0, input_window_end=45000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression"),
    ]
    res = evaluator.evaluate_decision(rel_res, state, forecasts)
    res_dict = res.to_dict()

    assert "control_action" not in res_dict
    assert "shutdown_command" not in res_dict
    assert "automatic_action" not in res_dict
    assert res.provenance.human_approval_required is True
