"""
Baseline Forecasting Implementations for FOUL-X M3.
Includes Persistence, Recent-Trend, and Moving Average baselines using common ForecastResult schema.
"""

import math
from typing import Optional, List
import pandas as pd
import numpy as np

from src.forecast.schemas import ForecastResult, ForecastStatus
from src.forecast.windows import get_causal_window


class PersistenceBaseline:
    """
    Naive Persistence Baseline: R_hat(t + h) = R_f(t).
    """

    def __init__(self, model_version: str = "1.0"):
        self.model_version = model_version

    def predict(self, rf_series: pd.Series, current_time: float, horizon_hours: int, exchanger_id: str = "E01") -> ForecastResult:
        window_slice, start_t, end_t = get_causal_window(rf_series, current_time, window_hours=1)
        
        reasons = []
        if current_time not in rf_series.index:
            reasons.append(f"MISSING_TIMESTEP:{current_time}")
            return ForecastResult(
                exchanger_id=exchanger_id,
                timestamp=current_time,
                horizon_hours=horizon_hours,
                prediction=None,
                input_window_start=start_t,
                input_window_end=end_t,
                status=ForecastStatus.UNAVAILABLE,
                unavailable_reasons=reasons,
                provenance=["R_f_derived"],
                method="Persistence",
                model_version=self.model_version,
            )

        current_val = float(rf_series.loc[current_time])

        if not math.isfinite(current_val):
            reasons.append("NONFINITE_CURRENT_VALUE")
            return ForecastResult(
                exchanger_id=exchanger_id,
                timestamp=current_time,
                horizon_hours=horizon_hours,
                prediction=None,
                input_window_start=start_t,
                input_window_end=end_t,
                status=ForecastStatus.INVALID_CURRENT_STATE,
                unavailable_reasons=reasons,
                provenance=["R_f_derived"],
                method="Persistence",
                model_version=self.model_version,
            )

        return ForecastResult(
            exchanger_id=exchanger_id,
            timestamp=current_time,
            horizon_hours=horizon_hours,
            prediction=current_val,
            input_window_start=start_t,
            input_window_end=end_t,
            status=ForecastStatus.SUCCESS,
            unavailable_reasons=[],
            provenance=["R_f_derived"],
            method="Persistence",
            model_version=self.model_version,
        )


class RecentTrendBaseline:
    """
    Recent Linear Trend Baseline: R_hat(t + h) = R_f(t) + h * slope(t-W:t).
    Uses training-only historical context window W (hours).
    """

    def __init__(self, trend_window_hours: int = 24, min_points: int = 3, model_version: str = "1.0"):
        self.trend_window_hours = trend_window_hours
        self.min_points = min_points
        self.model_version = model_version

    def predict(self, rf_series: pd.Series, current_time: float, horizon_hours: int, exchanger_id: str = "E01") -> ForecastResult:
        window_slice, start_t, end_t = get_causal_window(rf_series, current_time, self.trend_window_hours)
        reasons = []

        clean_slice = window_slice.dropna()
        clean_slice = clean_slice[np.isfinite(clean_slice)]

        if len(clean_slice) < self.min_points:
            reasons.append(f"INSUFFICIENT_HISTORY:found_{len(clean_slice)}_req_{self.min_points}")
            return ForecastResult(
                exchanger_id=exchanger_id,
                timestamp=current_time,
                horizon_hours=horizon_hours,
                prediction=None,
                input_window_start=start_t,
                input_window_end=end_t,
                status=ForecastStatus.INSUFFICIENT_HISTORY,
                unavailable_reasons=reasons,
                provenance=["R_f_derived"],
                method=f"RecentTrend_{self.trend_window_hours}h",
                model_version=self.model_version,
            )

        if current_time not in clean_slice.index:
            reasons.append("INVALID_CURRENT_STATE")
            return ForecastResult(
                exchanger_id=exchanger_id,
                timestamp=current_time,
                horizon_hours=horizon_hours,
                prediction=None,
                input_window_start=start_t,
                input_window_end=end_t,
                status=ForecastStatus.INVALID_CURRENT_STATE,
                unavailable_reasons=reasons,
                provenance=["R_f_derived"],
                method=f"RecentTrend_{self.trend_window_hours}h",
                model_version=self.model_version,
            )

        # Fit linear slope over time index: tau in [0, W]
        x = clean_slice.index.values - current_time  # Relative time (negative values <= 0)
        y = clean_slice.values

        if len(x) > 1 and np.var(x) > 0:
            slope, intercept = np.polyfit(x, y, 1)
        else:
            slope = 0.0

        current_val = float(clean_slice.loc[current_time])
        prediction = current_val + (slope * horizon_hours)

        return ForecastResult(
            exchanger_id=exchanger_id,
            timestamp=current_time,
            horizon_hours=horizon_hours,
            prediction=prediction,
            input_window_start=start_t,
            input_window_end=end_t,
            status=ForecastStatus.SUCCESS,
            unavailable_reasons=[],
            provenance=["R_f_derived"],
            method=f"RecentTrend_{self.trend_window_hours}h",
            model_version=self.model_version,
        )


class MovingAverageBaseline:
    """
    Causal Moving Average Baseline: MA(t, W) = mean(Rf(t-W+1), ..., Rf(t)).
    """

    def __init__(self, ma_window_hours: int = 24, min_points: int = 3, model_version: str = "1.0"):
        self.ma_window_hours = ma_window_hours
        self.min_points = min_points
        self.model_version = model_version

    def predict(self, rf_series: pd.Series, current_time: float, horizon_hours: int, exchanger_id: str = "E01") -> ForecastResult:
        window_slice, start_t, end_t = get_causal_window(rf_series, current_time, self.ma_window_hours)
        reasons = []

        clean_slice = window_slice.dropna()
        clean_slice = clean_slice[np.isfinite(clean_slice)]

        if len(clean_slice) < self.min_points:
            reasons.append(f"INSUFFICIENT_HISTORY:found_{len(clean_slice)}_req_{self.min_points}")
            return ForecastResult(
                exchanger_id=exchanger_id,
                timestamp=current_time,
                horizon_hours=horizon_hours,
                prediction=None,
                input_window_start=start_t,
                input_window_end=end_t,
                status=ForecastStatus.INSUFFICIENT_HISTORY,
                unavailable_reasons=reasons,
                provenance=["R_f_derived"],
                method=f"MovingAverage_{self.ma_window_hours}h",
                model_version=self.model_version,
            )

        ma_prediction = float(clean_slice.mean())

        return ForecastResult(
            exchanger_id=exchanger_id,
            timestamp=current_time,
            horizon_hours=horizon_hours,
            prediction=ma_prediction,
            input_window_start=start_t,
            input_window_end=end_t,
            status=ForecastStatus.SUCCESS,
            unavailable_reasons=[],
            provenance=["R_f_derived"],
            method=f"MovingAverage_{self.ma_window_hours}h",
            model_version=self.model_version,
        )
