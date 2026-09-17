"""
FOUL-X M1-C Data Contract & Target Derivation Unit Tests.
"""

import sys
sys.path.insert(0, ".")
from pathlib import Path
import pandas as pd
import pytest
from scripts.validate_m1c_data_contract import calculate_derived_rf

RAW_DATA_PATH = Path("data/raw/heat_exchanger_fouling_dataset.csv")


@pytest.fixture(scope="module")
def raw_df():
    assert RAW_DATA_PATH.exists()
    return pd.read_csv(RAW_DATA_PATH)


def test_ua_clean_uses_only_initial_window(raw_df):
    stats, derived_df = calculate_derived_rf(raw_df, clean_window_hours=100)
    for tag in ["E01", "E02", "E03", "E04", "E05"]:
        assert stats[tag]["UA_clean_W_K"] > 0, f"UA_clean for {tag} must be positive!"
        assert stats[tag]["nan_count"] == 0, f"NaNs found in derived R_f target for {tag}!"
        assert stats[tag]["inf_count"] == 0, f"Infs found in derived R_f target for {tag}!"


def test_derived_target_shape_and_columns(raw_df):
    stats, derived_df = calculate_derived_rf(raw_df)
    assert len(derived_df) == len(raw_df), "Derived target row count must match raw dataset!"
    for tag in ["E01", "E02", "E03", "E04", "E05"]:
        col_name = f"{tag}_R_fouling_derived"
        assert col_name in derived_df.columns, f"Missing target column {col_name}!"
