"""
Acceptance Unit Tests for FOUL-X M3 Baseline Forecasting & Causality.
"""

import sys
sys.path.insert(0, ".")
import math
from pathlib import Path
import pandas as pd
import numpy as np
import pytest

from src.forecast.schemas import ForecastResult, ForecastStatus
from src.forecast.windows import get_causal_window, validate_window_causality
from src.forecast.baselines import PersistenceBaseline, RecentTrendBaseline, MovingAverageBaseline
from src.forecast.metrics import compute_mae, compute_relative_improvement, evaluate_forecast_predictions

RAW_DATA_PATH = Path("data/raw/heat_exchanger_fouling_dataset.csv")


@pytest.fixture(scope="module")
def sample_rf_series():
    # Synthetic series t = 0 to 1000
    time = np.arange(0, 1001, dtype=float)
    # Slow linear drift + noise
    vals = 1e-5 + (0.5e-7 * time) + (1e-6 * np.sin(time / 10.0))
    return pd.Series(vals, index=time)


def test_moving_average_causality(sample_rf_series):
    ma_baseline = MovingAverageBaseline(ma_window_hours=24)
    current_time = 100.0
    res = ma_baseline.predict(sample_rf_series, current_time=current_time, horizon_hours=24)
    
    assert res.status == ForecastStatus.SUCCESS
    assert res.input_window_end == 100.0
    assert res.input_window_start == 77.0  # 100 - 24 + 1
    
    # Verify window causality
    assert validate_window_causality(sample_rf_series, current_time, 24)
    
    # Manually check that no values > 100 participated
    expected_mean = float(sample_rf_series.loc[77.0:100.0].mean())
    assert res.prediction == pytest.approx(expected_mean, rel=1e-6)


def test_recent_trend_causality(sample_rf_series):
    trend_baseline = RecentTrendBaseline(trend_window_hours=24)
    current_time = 200.0
    horizon = 24
    res = trend_baseline.predict(sample_rf_series, current_time=current_time, horizon_hours=horizon)

    assert res.status == ForecastStatus.SUCCESS
    assert res.input_window_end == 200.0
    assert res.input_window_start == 177.0

    # Verify no values > 200 participated
    window_slice, _, _ = get_causal_window(sample_rf_series, current_time, 24)
    assert window_slice.index.max() == 200.0
    assert res.prediction is not None


def test_invalid_current_state_no_silent_imputation(sample_rf_series):
    # Create corrupted series with NaN at current_time
    corrupted_series = sample_rf_series.copy()
    corrupted_series.loc[300.0] = float("nan")

    persistence = PersistenceBaseline()
    res = persistence.predict(corrupted_series, current_time=300.0, horizon_hours=24)

    assert res.status == ForecastStatus.INVALID_CURRENT_STATE
    assert res.prediction is None
    assert len(res.unavailable_reasons) > 0
    assert "NONFINITE_CURRENT_VALUE" in res.unavailable_reasons[0]


def test_persistence_correctness(sample_rf_series):
    persistence = PersistenceBaseline()
    res = persistence.predict(sample_rf_series, current_time=50.0, horizon_hours=72)

    assert res.status == ForecastStatus.SUCCESS
    assert res.prediction == sample_rf_series.loc[50.0]


def test_common_forecast_result_schema(sample_rf_series):
    persistence = PersistenceBaseline()
    res = persistence.predict(sample_rf_series, current_time=50.0, horizon_hours=24, exchanger_id="E02")

    assert isinstance(res, ForecastResult)
    assert res.exchanger_id == "E02"
    assert res.horizon_hours == 24
    assert res.method == "Persistence"
    assert res.target_definition == "R_f_derived(t+h)"


def test_relative_improvement_calculation():
    mae_pers = 2.0e-5
    mae_trend = 1.5e-5
    rel_imp = compute_relative_improvement(mae_pers, mae_trend)
    # (2e-5 - 1.5e-5) / 2e-5 = 0.5e-5 / 2e-5 = 0.25 (25% improvement)
    assert rel_imp == pytest.approx(0.25, rel=1e-5)


def test_chronological_split_preservation():
    raw_df = pd.read_csv(RAW_DATA_PATH)
    t_train = raw_df.loc[raw_df["Time_hr"] <= 44799, "Time_hr"]
    t_val = raw_df.loc[(raw_df["Time_hr"] >= 44800) & (raw_df["Time_hr"] <= 54399), "Time_hr"]
    t_test = raw_df.loc[raw_df["Time_hr"] >= 54400, "Time_hr"]

    assert t_train.max() < t_val.min(), "Train time must strictly precede Validation time!"
    assert t_val.max() < t_test.min(), "Validation time must strictly precede Test time!"


def test_deterministic_forecast_execution(sample_rf_series):
    trend_baseline = RecentTrendBaseline(trend_window_hours=24)
    res1 = trend_baseline.predict(sample_rf_series, current_time=150.0, horizon_hours=24)
    res2 = trend_baseline.predict(sample_rf_series, current_time=150.0, horizon_hours=24)

    assert res1.model_dump() == res2.model_dump(), "Forecast predictions must be 100% deterministic!"
