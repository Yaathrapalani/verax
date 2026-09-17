import pytest
import pandas as pd
import numpy as np

from src.physics.state_estimator import PhysicsStateEstimator
from src.forecast.schemas import ForecastResult, ForecastStatus
from src.foulx.gate import (
    ReliabilityGateEvaluator,
    HistoricalRegimeSupportChecker,
    GateStatus,
    ReliabilityReasonCode,
)

def test_evaluator_pass_scenario():
    # Setup state estimator
    estimator = PhysicsStateEstimator()
    ref_ua = {"E01": 207061.2}
    estimator.ua_clean_references = ref_ua

    raw_record = {
        "E01_Crude_Tube_T_In_degC": 150.8,
        "E01_Crude_Tube_T_Out_degC": 195.6,
        "E01_HeavyNaphtha_Shell_T_In_degC": 249.5,
        "E01_HeavyNaphtha_Shell_T_Out_degC": 188.2,
        "E01_Crude_Tube_m_kg_s": 98.6,
        "E01_HeavyNaphtha_Shell_m_kg_s": 80.2,
        "E01_Crude_Tube_Cp_J_kgK": 2100.0,
        "E01_HeavyNaphtha_Shell_Cp_J_kgK": 1900.0,
    }

    state = estimator.process_record(raw_record, "E01")

    forecast_res = ForecastResult(
        exchanger_id="E01",
        timestamp=100.0,
        horizon_hours=24,
        prediction=7.2e-8,
        input_window_start=76.0,
        input_window_end=100.0,
        status=ForecastStatus.SUCCESS,
        method="RidgeRegression",
    )

    evaluator = ReliabilityGateEvaluator()
    res = evaluator.evaluate_reliability(
        raw_record=raw_record,
        required_fields=list(raw_record.keys()),
        tag="E01",
        shell_name="HeavyNaphtha",
        canonical_state=state,
        forecast_result=forecast_res,
    )

    assert res.status == GateStatus.PASS
    assert len(res.reason_codes) == 0
    assert res.exchanger_id == "E01"
    assert res.forecast_reference.prediction == 7.2e-8
