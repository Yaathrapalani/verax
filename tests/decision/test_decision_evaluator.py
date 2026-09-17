import pytest
from src.physics.schemas import CanonicalExchangerState, ThermalState, FoulingState, DataQualityState, StateValidity, AvailabilityState, ProvenanceState
from src.forecast.schemas import ForecastResult, ForecastStatus
from src.foulx.gate.schemas import ReliabilityResult, GateStatus, ForecastReference, GateProvenance
from src.foulx.decision import (
    DecisionEngineEvaluator,
    DecisionState,
    DecisionReasonCode,
    DecisionThresholdConfig,
)

def create_mock_canonical_state(rf_val: float = 7.2e-8) -> CanonicalExchangerState:
    return CanonicalExchangerState(
        timestamp=45000.0,
        exchanger_id="E01",
        thermal=ThermalState(q_tube=9.2e6, q_shell=9.3e6, lmtd=45.0, ua=203000.0, ua_clean_reference=207000.0),
        fouling=FoulingState(rf_derived=rf_val, rf_relative_to_reference=0.98),
        data_quality=DataQualityState(valid_input_count=6, invalid_input_count=0, primary_status=StateValidity.VALID, reasons=[]),
        availability=AvailabilityState(),
        provenance=ProvenanceState(),
    )

def create_mock_reliability_result(status: GateStatus = GateStatus.PASS) -> ReliabilityResult:
    return ReliabilityResult(
        timestamp=45000.0,
        exchanger_id="E01",
        status=status,
        checks=[],
        reason_codes=[],
        evidence={},
        forecast_reference=ForecastReference(exchanger_id="E01", timestamp=45000.0, horizon_hours=24, prediction=1.0e-7),
        provenance=GateProvenance(),
    )

def test_evaluator_operate_case():
    evaluator = DecisionEngineEvaluator()
    rel_res = create_mock_reliability_result(GateStatus.PASS)
    state = create_mock_canonical_state(rf_val=7.2e-8)
    forecasts = [
        ForecastResult(exchanger_id="E01", timestamp=45000.0, horizon_hours=1, prediction=7.5e-8, input_window_start=44999.0, input_window_end=45000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression"),
        ForecastResult(exchanger_id="E01", timestamp=45000.0, horizon_hours=6, prediction=8.5e-8, input_window_start=44994.0, input_window_end=45000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression"),
        ForecastResult(exchanger_id="E01", timestamp=45000.0, horizon_hours=24, prediction=1.1e-7, input_window_start=44976.0, input_window_end=45000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression"),
    ]

    res = evaluator.evaluate_decision(rel_res, state, forecasts)
    assert res.decision == DecisionState.OPERATE
    assert res.threshold_crossing is False
    assert res.reason_codes == [DecisionReasonCode.THRESHOLD_NOT_REACHED]

def test_evaluator_cleaning_review_case():
    evaluator = DecisionEngineEvaluator()
    rel_res = create_mock_reliability_result(GateStatus.PASS)
    state = create_mock_canonical_state(rf_val=7.2e-8)
    forecasts = [
        ForecastResult(exchanger_id="E01", timestamp=45000.0, horizon_hours=1, prediction=7.5e-8, input_window_start=44999.0, input_window_end=45000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression"),
        ForecastResult(exchanger_id="E01", timestamp=45000.0, horizon_hours=6, prediction=1.6e-7, input_window_start=44994.0, input_window_end=45000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression"),
        ForecastResult(exchanger_id="E01", timestamp=45000.0, horizon_hours=24, prediction=2.1e-7, input_window_start=44976.0, input_window_end=45000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression"),
    ]

    res = evaluator.evaluate_decision(rel_res, state, forecasts)
    assert res.decision == DecisionState.CLEANING_REVIEW
    assert res.threshold_crossing is True
    assert res.estimated_crossing_horizon_hours == 6
    assert res.reason_codes == [DecisionReasonCode.THRESHOLD_REACHED]

def test_evaluator_exact_threshold_equality():
    evaluator = DecisionEngineEvaluator()
    rel_res = create_mock_reliability_result(GateStatus.PASS)
    state = create_mock_canonical_state(rf_val=7.2e-8)
    cfg = DecisionThresholdConfig(rf_threshold=1.5e-7, planning_horizon_hours=24, exchanger_id="E01")
    
    # Exact threshold equality: Rf(t+24) == 1.5e-7
    forecasts = [
        ForecastResult(exchanger_id="E01", timestamp=45000.0, horizon_hours=24, prediction=1.5e-7, input_window_start=44976.0, input_window_end=45000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression"),
    ]

    res = evaluator.evaluate_decision(rel_res, state, forecasts, threshold_config=cfg)
    assert res.decision == DecisionState.CLEANING_REVIEW
    assert res.threshold_crossing is True
    assert res.estimated_crossing_horizon_hours == 24
