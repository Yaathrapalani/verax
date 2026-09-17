import pytest
import pandas as pd
import numpy as np

from src.physics.state_estimator import PhysicsStateEstimator
from src.physics.schemas import StateValidity, CanonicalExchangerState
from src.forecast.schemas import ForecastResult, ForecastStatus
from src.foulx.gate import (
    ReliabilityGateEvaluator,
    HistoricalRegimeSupportChecker,
    GateStatus,
    ReliabilityReasonCode,
    REASON_CODE_ORDER,
)

def test_safety_invariants_and_reason_code_order():
    estimator = PhysicsStateEstimator({"E01": 207061.2})

    # Record missing required field AND containing NaN AND invalid physics
    raw_record_corrupted = {
        "E01_Crude_Tube_T_In_degC": float("nan"),
        # Missing E01_Crude_Tube_T_Out_degC
        "E01_HeavyNaphtha_Shell_T_In_degC": 249.5,
        "E01_HeavyNaphtha_Shell_T_Out_degC": 188.2,
        "E01_Crude_Tube_m_kg_s": 98.6,
        "E01_HeavyNaphtha_Shell_m_kg_s": 80.2,
        "E01_Crude_Tube_Cp_J_kgK": 2100.0,
        "E01_HeavyNaphtha_Shell_Cp_J_kgK": 1900.0,
    }

    state_invalid = estimator.process_record(raw_record_corrupted, "E01")

    forecast_res = ForecastResult(
        exchanger_id="E01",
        timestamp=100.0,
        horizon_hours=24,
        prediction=None,
        input_window_start=76.0,
        input_window_end=100.0,
        status=ForecastStatus.INVALID_CURRENT_STATE,
        method="RidgeRegression",
    )

    required_fields = list(raw_record_corrupted.keys()) + ["E01_Crude_Tube_T_Out_degC"]

    evaluator = ReliabilityGateEvaluator()
    res = evaluator.evaluate_reliability(
        raw_record=raw_record_corrupted,
        required_fields=required_fields,
        tag="E01",
        shell_name="HeavyNaphtha",
        canonical_state=state_invalid,
        forecast_result=forecast_res,
    )

    # SAFETY INVARIANT 1: Must ABSTAIN if any check fails
    assert res.status == GateStatus.ABSTAIN
    assert len(res.reason_codes) >= 2

    # SAFETY INVARIANT 2: Deterministic Ordering
    # DATA_INCOMPLETE must come before SENSOR_INVALID, which comes before PHYSICS_INCONSISTENT
    indices = [REASON_CODE_ORDER.index(code) for code in res.reason_codes]
    assert indices == sorted(indices), "Reason codes must appear in exact deterministic order!"

def test_abstain_never_issues_command():
    """Ensure no command or action fields exist in ReliabilityResult."""
    estimator = PhysicsStateEstimator({"E01": 207061.2})
    raw_record = {"E01_Crude_Tube_T_In_degC": float("nan")}
    state = estimator.process_record(raw_record, "E01")
    forecast_res = ForecastResult(
        exchanger_id="E01",
        timestamp=100.0,
        horizon_hours=24,
        prediction=None,
        input_window_start=76.0,
        input_window_end=100.0,
        status=ForecastStatus.UNAVAILABLE,
        method="RidgeRegression",
    )
    evaluator = ReliabilityGateEvaluator()
    res = evaluator.evaluate_reliability(
        raw_record=raw_record,
        required_fields=["E01_Crude_Tube_T_In_degC", "E01_Crude_Tube_m_kg_s"],
        tag="E01",
        shell_name="HeavyNaphtha",
        canonical_state=state,
        forecast_result=forecast_res,
    )
    res_dict = res.to_dict()
    assert "command" not in res_dict
    assert "cleaning_action" not in res_dict
    assert "shutdown" not in res_dict
