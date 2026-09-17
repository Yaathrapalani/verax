"""
FOUL-X Forecasting Package.
"""

from src.forecast.schemas import ForecastStatus, ForecastResult
from src.forecast.targets import construct_target_series, extract_target_value
from src.forecast.windows import get_causal_window, validate_window_causality
from src.forecast.baselines import PersistenceBaseline, RecentTrendBaseline, MovingAverageBaseline
from src.forecast.metrics import (
    compute_mae,
    compute_rmse,
    compute_smape,
    compute_r2,
    compute_mbe,
    compute_relative_improvement,
    evaluate_forecast_predictions,
)

__all__ = [
    "ForecastStatus",
    "ForecastResult",
    "construct_target_series",
    "extract_target_value",
    "get_causal_window",
    "validate_window_causality",
    "PersistenceBaseline",
    "RecentTrendBaseline",
    "MovingAverageBaseline",
    "compute_mae",
    "compute_rmse",
    "compute_smape",
    "compute_r2",
    "compute_mbe",
    "compute_relative_improvement",
    "evaluate_forecast_predictions",
]
