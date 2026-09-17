import pytest
import pandas as pd
from src.physics.schemas import CanonicalExchangerState, ThermalState, FoulingState, DataQualityState, StateValidity, AvailabilityState, ProvenanceState
from src.forecast.schemas import ForecastResult, ForecastStatus
from src.foulx.gate.evaluator import ReliabilityGateEvaluator
from src.foulx.gate.checks import HistoricalRegimeSupportChecker
from src.foulx.decision.evaluator import DecisionEngineEvaluator
from src.foulx.decision.thresholds import DecisionThresholdConfig
from src.foulx.evaluation.schemas import PolicyType, EvaluationCondition, GateStatus, DecisionState
from src.foulx.evaluation.evaluator import PolicyExperimentEvaluator
from src.foulx.evaluation.perturbations import SyntheticRegimeShiftPerturber

def create_mock_instance(t: float = 55000.0, current_rf: float = 7.0e-8, actual_rf: float = 1.6e-7):
    state = CanonicalExchangerState(
        timestamp=t,
        exchanger_id="E01",
        thermal=ThermalState(q_tube=9.0e6, q_shell=9.0e6, lmtd=45.0, ua=200000.0, ua_clean_reference=205000.0),
        fouling=FoulingState(rf_derived=current_rf, rf_relative_to_reference=0.98),
        data_quality=DataQualityState(valid_input_count=6, invalid_input_count=0, primary_status=StateValidity.VALID, reasons=[]),
        availability=AvailabilityState(),
        provenance=ProvenanceState(),
    )
    forecasts = [
        ForecastResult(exchanger_id="E01", timestamp=t, horizon_hours=24, prediction=1.7e-7, input_window_start=t-24, input_window_end=t, status=ForecastStatus.SUCCESS, method="RidgeRegression")
    ]
    raw_record = {
        "E01_Crude_Tube_T_In_degC": 150.0,
        "E01_Crude_Tube_T_Out_degC": 200.0,
        "E01_Shell_Shell_T_In_degC": 300.0,
        "E01_Shell_Shell_T_Out_degC": 250.0,
        "E01_Crude_Tube_m_kg_s": 50.0,
        "E01_Shell_Shell_m_kg_s": 50.0,
    }
    feat_vec = pd.Series({"Crude_Tube_T_In_degC": 150.0, "Crude_Tube_m_kg_s": 50.0})
    return {
        "raw_record": raw_record,
        "required_fields": list(raw_record.keys()),
        "tag": "E01",
        "shell_name": "Shell",
        "canonical_state": state,
        "forecast_results": forecasts,
        "feature_vector": feat_vec,
        "actual_future_rf": actual_rf,
    }

def test_evaluator_supported_vs_shifted():
    # Fit regime checker on training dummy
    regime_checker = HistoricalRegimeSupportChecker(z_score_threshold=4.0)
    train_df = pd.DataFrame({"Crude_Tube_T_In_degC": [150.0]*10, "Crude_Tube_m_kg_s": [50.0]*10})
    regime_checker.fit_on_training_data(train_df)

    gate_eval = ReliabilityGateEvaluator(regime_checker=regime_checker)
    dec_eval = DecisionEngineEvaluator()
    cfg = DecisionThresholdConfig(rf_threshold=1.5e-7, planning_horizon_hours=24, exchanger_id="E01")
    perturber = SyntheticRegimeShiftPerturber(shift_factor=10.0)

    evaluator = PolicyExperimentEvaluator(gate_eval, dec_eval, cfg, perturber)

    inst = create_mock_instance()

    # 1. Supported condition
    res_sup = evaluator.evaluate_single_instance(
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

    assert res_sup.gate_status == GateStatus.PASS
    assert res_sup.fallback_used is False
    assert res_sup.predicted_action == DecisionState.CLEANING_REVIEW

    # 2. Shifted condition
    res_shift = evaluator.evaluate_single_instance(
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

    assert res_shift.gate_status == GateStatus.ABSTAIN
    assert res_shift.fallback_used is True
    assert res_shift.predicted_action == DecisionState.ABSTAIN
