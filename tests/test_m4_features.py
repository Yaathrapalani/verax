"""
Unit tests for FOUL-X M4.0 Causal Feature Engineering.
"""

import sys
sys.path.insert(0, ".")
from pathlib import Path
import pandas as pd
import pytest

from src.physics.state_estimator import PhysicsStateEstimator
from src.models.features import extract_causal_features_for_exchanger
from src.models.schemas import FeatureConfig

RAW_DATA_PATH = Path("data/raw/heat_exchanger_fouling_dataset.csv")


@pytest.fixture(scope="module")
def raw_df():
    assert RAW_DATA_PATH.exists()
    return pd.read_csv(RAW_DATA_PATH)


@pytest.fixture(scope="module")
def estimator(raw_df):
    est = PhysicsStateEstimator()
    est.fit_baseline_from_dataframe(raw_df, clean_window_hours=100)
    return est


def test_causal_feature_generation_shape_and_columns(raw_df, estimator):
    config = FeatureConfig()
    X_df, y_series = extract_causal_features_for_exchanger(raw_df, "E01", estimator, config)

    assert len(X_df) == len(raw_df)
    assert len(y_series) == len(raw_df)
    assert "Rf_derived_t" in X_df.columns
    assert "Crude_API" in X_df.columns
    assert "Rf_mean_24h" in X_df.columns
    assert "Rf_slope_24h" in X_df.columns
    assert "delta_Rf_1h" in X_df.columns


def test_feature_window_sizes(raw_df, estimator):
    config = FeatureConfig(window_sizes=[6, 24, 72, 168])
    X_df, _ = extract_causal_features_for_exchanger(raw_df, "E01", estimator, config)

    for w in [6, 24, 72, 168]:
        assert f"Rf_mean_{w}h" in X_df.columns
        assert f"Rf_std_{w}h" in X_df.columns
        assert f"Rf_min_{w}h" in X_df.columns
        assert f"Rf_max_{w}h" in X_df.columns
        assert f"Rf_delta_{w}h" in X_df.columns
        assert f"Rf_slope_{w}h" in X_df.columns
