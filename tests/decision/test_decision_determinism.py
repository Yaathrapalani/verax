import pytest
from src.forecast.schemas import ForecastResult, ForecastStatus
from src.foulx.gate.schemas import GateStatus
from src.foulx.decision import DecisionEngineEvaluator
from tests.decision.test_decision_evaluator import create_mock_canonical_state, create_mock_reliability_result

def test_evaluator_determinism():
    evaluator = DecisionEngineEvaluator()
    rel_res = create_mock_reliability_result(GateStatus.PASS)
    state = create_mock_canonical_state(rf_val=7.2e-8)
    forecasts = [
        ForecastResult(exchanger_id="E01", timestamp=45000.0, horizon_hours=1, prediction=7.5e-8, input_window_start=44999.0, input_window_end=45000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression"),
        ForecastResult(exchanger_id="E01", timestamp=45000.0, horizon_hours=6, prediction=8.5e-8, input_window_start=44994.0, input_window_end=45000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression"),
        ForecastResult(exchanger_id="E01", timestamp=45000.0, horizon_hours=24, prediction=1.1e-7, input_window_start=44976.0, input_window_end=45000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression"),
    ]

    res1 = evaluator.evaluate_decision(rel_res, state, forecasts)
    res2 = evaluator.evaluate_decision(rel_res, state, forecasts)

    assert res1.model_dump() == res2.model_dump(), "Decision Engine evaluation must be 100% deterministic!"
