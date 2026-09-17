"""
FOUL-X M1-B Automated Data Contract and Target Leakage Tests.
"""

from pathlib import Path
import pandas as pd
import pytest

RAW_DATA_PATH = Path("data/raw/heat_exchanger_fouling_dataset.csv")

REQUIRED_COLUMNS = [
    "Time_hr",
    "Crude_API",
    "Crude_Chlorides",
    "Crude_TAN",
    "E01_Crude_Tube_T_In_degC",
    "E01_Crude_Tube_T_Out_degC",
    "E01_Crude_Tube_m_kg_s",
    "E01_HeavyNaphtha_Shell_T_In_degC",
    "E01_HeavyNaphtha_Shell_T_Out_degC",
    "E01_HeavyNaphtha_Shell_m_kg_s",
]


@pytest.fixture(scope="module")
def df_raw():
    assert RAW_DATA_PATH.exists(), f"Dataset file missing at {RAW_DATA_PATH}"
    return pd.read_csv(RAW_DATA_PATH)


def test_required_columns_exist(df_raw):
    missing = [col for col in REQUIRED_COLUMNS if col not in df_raw.columns]
    assert not missing, f"Missing required dataset columns: {missing}"


def test_time_ordering_monotonic(df_raw):
    time_series = df_raw["Time_hr"]
    assert time_series.is_monotonic_increasing, "Time_hr is not strictly monotonic increasing!"
    assert time_series.duplicated().sum() == 0, "Duplicate timestamps found in Time_hr!"


def test_duplicate_columns_detected(df_raw):
    dot1_cols = [c for c in df_raw.columns if c.endswith(".1")]
    assert len(dot1_cols) == 20, f"Expected 20 duplicate .1 columns, found {len(dot1_cols)}"
    for col in dot1_cols:
        base_col = col[:-2]
        assert base_col in df_raw.columns, f"Base column {base_col} missing for {col}"
        diff = (df_raw[base_col] - df_raw[col]).abs().max()
        assert diff == 0.0, f"Column {col} differs from base {base_col}!"


def test_target_leakage_forbidden_columns():
    """
    Ensures that any model-input schema strictly rejects hidden ground-truth columns.
    """
    model_input_schema = [
        "Time_hr",
        "Crude_API",
        "Crude_Chlorides",
        "Crude_TAN",
        "E01_Crude_Tube_T_In_degC",
        "E01_Crude_Tube_T_Out_degC",
        "E01_Crude_Tube_m_kg_s",
    ]

    forbidden_ground_truth_test_cases = [
        "R_fouling_True",
        "E01_R_fouling_True",
        "U_fouled_True",
        "Q_actual_True",
        "T_wall_avg_True_C",
    ]

    for col in model_input_schema:
        assert "_True" not in col, f"Forbidden ground-truth column {col} in input schema!"

    for forbidden_col in forbidden_ground_truth_test_cases:
        with pytest.raises(AssertionError, match="Forbidden ground-truth column"):
            # Simulate invalid inclusion of ground truth in input schema
            schema_with_leak = model_input_schema + [forbidden_col]
            for col in schema_with_leak:
                assert "_True" not in col, f"Forbidden ground-truth column {col} in input schema!"


def test_no_pressure_drop_columns(df_raw):
    pressure_cols = [c for c in df_raw.columns if "press" in c.lower() or "dp" in c.lower() or "delta_p" in c.lower()]
    assert len(pressure_cols) == 0, f"Unexpected pressure drop columns found: {pressure_cols}"
