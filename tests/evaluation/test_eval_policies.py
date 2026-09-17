import pytest
import pandas as pd
from src.physics.schemas import CanonicalExchangerState, ThermalState, FoulingState, DataQualityState, StateValidity, AvailabilityState, ProvenanceState
from src.forecast.schemas import ForecastResult, ForecastStatus
from src.foulx.gate.schemas import GateStatus
from src.foulx.gate.evaluator import ReliabilityGateEvaluator
from src.foulx.decision.schemas import DecisionState
from src.foulx.decision.evaluator import DecisionEngineEvaluator
from src.foulx.decision.thresholds import DecisionThresholdConfig
from src.foulx.evaluation.policies import FixedPolicy, UngatedPolicy, GatedPolicy

def create_mock_state(rf_val: float = 7.0e-8) -> CanonicalExchangerState:
    return CanonicalExchangerState(
        timestamp=55000.0,
        exchanger_id="E01",
        thermal=ThermalState(q_tube=9.0e6, q_shell=9.0e6, lmtd=45.0, ua=200000.0, ua_clean_reference=205000.0),
        fouling=FoulingState(rf_derived=rf_val, rf_relative_to_reference=0.98),
        data_quality=DataQualityState(valid_input_count=6, invalid_input_count=0, primary_status=StateValidity.VALID, reasons=[]),
        availability=AvailabilityState(),
        provenance=ProvenanceState(),
    )

def test_fixed_policy_rule():
    cfg = DecisionThresholdConfig(rf_threshold=1.5e-7, planning_horizon_hours=24, exchanger_id="E01")
    fixed = FixedPolicy(cfg)
    assert fixed.evaluate(current_rf=1.0e-7, timestamp=55000.0) == DecisionState.OPERATE
    assert fixed.evaluate(current_rf=1.6e-7, timestamp=55000.0) == DecisionState.CLEANING_REVIEW

def test_ungated_policy_bypasses_gate():
    cfg = DecisionThresholdConfig(rf_threshold=1.5e-7, planning_horizon_hours=24, exchanger_id="E01")
    dec_eval = DecisionEngineEvaluator()
    ungated = UngatedPolicy(dec_eval)
    state = create_mock_state(7.0e-8)
    forecasts = [
        ForecastResult(exchanger_id="E01", timestamp=55000.0, horizon_hours=24, prediction=1.8e-7, input_window_start=54976.0, input_window_end=55000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression")
    ]
    res = ungated.evaluate(canonical_state=state, forecast_results=forecasts, threshold_config=cfg)
    assert res.decision == DecisionState.CLEANING_REVIEW
    assert res.reliability_status == GateStatus.PASS

def test_gated_policy_fallback_on_abstain():
    cfg = DecisionThresholdConfig(rf_threshold=1.5e-7, planning_horizon_hours=24, exchanger_id="E01")
    gate_eval = ReliabilityGateEvaluator() # no regime checker -> invalid required field test
    dec_eval = DecisionEngineEvaluator()
    fixed = FixedPolicy(cfg)
    gated = GatedPolicy(gate_eval, dec_eval, fixed)

    state = create_mock_state(7.0e-8)
    forecasts = [
        ForecastResult(exchanger_id="E01", timestamp=55000.0, horizon_hours=24, prediction=1.8e-7, input_window_start=54976.0, input_window_end=55000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression")
    ]
    # Missing required field triggers ABSTAIN
    raw_record = {"E01_Crude_Tube_T_In_degC": 150.0} # Missing other fields
    res = gated.evaluate(
        raw_record=raw_record,
        required_fields=["E01_Crude_Tube_T_In_degC", "E01_Crude_Tube_m_kg_s"],
        tag="E01",
        shell_name="E01_Shell",
        canonical_state=state,
        forecast_results=forecasts,
        feature_vector=None,
        threshold_config=cfg,
    )

    assert res["reliability_result"].status == GateStatus.ABSTAIN
    assert res["fallback_used"] is True
    assert res["action"] == DecisionState.OPERATE # Fallback to FIXED policy on current_rf=7e-8 (<1.5e-7)
