"""
Integration and Acceptance Tests for FOUL-X Physics State Estimator.
"""

import sys
sys.path.insert(0, ".")
from pathlib import Path
import pandas as pd
import pytest

from src.physics.schemas import StateValidity, CanonicalExchangerState
from src.physics.state_estimator import PhysicsStateEstimator, EXCHANGER_MAPPING

RAW_DATA_PATH = Path("data/raw/heat_exchanger_fouling_dataset.csv")


@pytest.fixture(scope="module")
def df_raw():
    assert RAW_DATA_PATH.exists()
    return pd.read_csv(RAW_DATA_PATH)


@pytest.fixture(scope="module")
def estimator(df_raw):
    est = PhysicsStateEstimator()
    est.fit_baseline_from_dataframe(df_raw, clean_window_hours=100)
    return est


def test_exchanger_specific_ua_clean_references(estimator):
    refs = estimator.ua_clean_references
    assert len(refs) == 5, "Must contain references for all 5 exchangers!"
    for tag in ["E01", "E02", "E03", "E04", "E05"]:
        assert tag in refs, f"Missing UA_clean_reference for {tag}"
        assert refs[tag] > 100000.0, f"UA_clean_reference for {tag} should be physically plausible!"
    
    # Verify references are independent and not identical
    ref_values = set(refs.values())
    assert len(ref_values) == 5, "Exchanger-specific UA_clean references must be distinct!"


def test_support_all_five_exchangers(estimator, df_raw):
    sample_record = df_raw.iloc[0].to_dict()
    for tag in ["E01", "E02", "E03", "E04", "E05"]:
        state = estimator.process_record(sample_record, tag)
        assert isinstance(state, CanonicalExchangerState)
        assert state.exchanger_id == tag
        assert state.data_quality.primary_status == StateValidity.VALID
        assert state.thermal.ua > 0
        assert state.fouling.rf_derived is not None


def test_multiple_simultaneous_invalidity_reasons(estimator, df_raw):
    corrupted_record = df_raw.iloc[0].to_dict()
    # Corrupt mass flow (zero flow) and introduce NaN in temperature
    corrupted_record["E01_Crude_Tube_m_kg_s"] = 0.0
    corrupted_record["E01_Crude_Tube_T_In_degC"] = float("nan")

    state = estimator.process_record(corrupted_record, "E01")
    assert state.data_quality.primary_status != StateValidity.VALID
    assert len(state.data_quality.reasons) >= 2, "Must preserve multiple failure reasons!"
    assert any("NONFINITE" in r for r in state.data_quality.reasons)


def test_no_silent_repair(estimator, df_raw):
    corrupted_record = df_raw.iloc[0].to_dict()
    corrupted_record["E01_Crude_Tube_T_Out_degC"] = float("nan")

    state = estimator.process_record(corrupted_record, "E01")
    assert state.data_quality.primary_status == StateValidity.INVALID_INPUT
    assert state.thermal.q_tube is None, "Invalid inputs must NOT be silently repaired to 0.0!"
    assert state.thermal.ua is None, "Invalid inputs must NOT produce a repaired UA!"


def test_single_state_determinism(estimator, df_raw):
    record = df_raw.iloc[100].to_dict()
    state1 = estimator.process_record(record, "E01")
    state2 = estimator.process_record(record, "E01")
    assert state1.model_dump() == state2.model_dump(), "State estimator must be 100% deterministic!"


def test_batch_and_single_state_consistency(estimator, df_raw):
    sub_df = df_raw.head(5)
    batch_states = estimator.process_dataframe(sub_df)
    
    # Verify count: 5 rows * 5 exchangers = 25 states
    assert len(batch_states) == 25
    
    # Check first record for E01
    single_state = estimator.process_record(sub_df.iloc[0].to_dict(), "E01")
    matching_batch_state = [s for s in batch_states if s.timestamp == single_state.timestamp and s.exchanger_id == "E01"][0]
    assert single_state.model_dump() == matching_batch_state.model_dump()


def test_no_hidden_true_variable_leakage(estimator, df_raw):
    record = df_raw.iloc[0].to_dict()
    state = estimator.process_record(record, "E01")
    state_dict = state.to_dict()

    # Recursively check keys in state dictionary to ensure no *_True columns are present
    def check_keys(d):
        if isinstance(d, dict):
            for k, v in d.items():
                assert not str(k).endswith("_True"), f"Leaked forbidden variable pattern {k}!"
                check_keys(v)
        elif isinstance(d, list):
            for item in d:
                check_keys(item)

    check_keys(state_dict)
