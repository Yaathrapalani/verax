import pytest
import pandas as pd
import numpy as np

from src.foulx.gate.checks import (
    check_data_completeness,
    check_sensor_validity,
    check_physics_consistency,
    HistoricalRegimeSupportChecker,
)
from src.foulx.gate.schemas import CheckStatus
from src.foulx.gate.reason_codes import ReliabilityReasonCode
from src.physics.state_estimator import PhysicsStateEstimator
from src.physics.schemas import StateValidity

def test_check_data_completeness():
    required = ["E01_Crude_Tube_T_In_degC", "E01_Crude_Tube_m_kg_s"]
    valid_record = {"E01_Crude_Tube_T_In_degC": 150.0, "E01_Crude_Tube_m_kg_s": 98.5}
    
    res_pass = check_data_completeness(valid_record, required)
    assert res_pass.status == CheckStatus.PASS
    assert res_pass.reason_code is None
    
    incomplete_record = {"E01_Crude_Tube_T_In_degC": 150.0}
    res_fail = check_data_completeness(incomplete_record, required)
    assert res_fail.status == CheckStatus.FAIL
    assert res_fail.reason_code == ReliabilityReasonCode.DATA_INCOMPLETE
    assert "E01_Crude_Tube_m_kg_s" in res_fail.evidence["missing_fields"]

def test_check_sensor_validity():
    tag = "E01"
    shell_name = "HeavyNaphtha"
    
    valid_record = {
        f"{tag}_Crude_Tube_T_In_degC": 150.0,
        f"{tag}_Crude_Tube_T_Out_degC": 195.0,
        f"{tag}_{shell_name}_Shell_T_In_degC": 250.0,
        f"{tag}_{shell_name}_Shell_T_Out_degC": 188.0,
        f"{tag}_Crude_Tube_m_kg_s": 98.0,
        f"{tag}_{shell_name}_Shell_m_kg_s": 80.0,
    }
    
    res_pass = check_sensor_validity(valid_record, tag, shell_name)
    assert res_pass.status == CheckStatus.PASS
    
    nan_record = valid_record.copy()
    nan_record[f"{tag}_Crude_Tube_T_In_degC"] = float("nan")
    res_fail = check_sensor_validity(nan_record, tag, shell_name)
    assert res_fail.status == CheckStatus.FAIL
    assert res_fail.reason_code == ReliabilityReasonCode.SENSOR_INVALID
    
    out_of_bounds = valid_record.copy()
    out_of_bounds[f"{tag}_Crude_Tube_T_In_degC"] = 999.0
    res_bounds = check_sensor_validity(out_of_bounds, tag, shell_name)
    assert res_bounds.status == CheckStatus.FAIL
    assert res_bounds.reason_code == ReliabilityReasonCode.SENSOR_INVALID

def test_regime_support_checker_train_only():
    np.random.seed(42)
    X_train = pd.DataFrame({
        "f1": np.random.normal(10.0, 1.0, 1000),
        "f2": np.random.normal(50.0, 5.0, 1000),
    })
    
    checker = HistoricalRegimeSupportChecker(z_score_threshold=4.0)
    checker.fit_on_training_data(X_train)
    assert checker.is_fitted
    
    # Supported sample
    valid_vec = pd.Series({"f1": 10.5, "f2": 51.0})
    res_pass = checker.check_regime_support(valid_vec)
    assert res_pass.status == CheckStatus.PASS
    
    # OOD sample (> 4 std)
    ood_vec = pd.Series({"f1": 25.0, "f2": 51.0})
    res_fail = checker.check_regime_support(ood_vec)
    assert res_fail.status == CheckStatus.FAIL
    assert res_fail.reason_code == ReliabilityReasonCode.REGIME_OOD
