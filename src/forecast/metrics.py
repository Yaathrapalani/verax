"""
Safe Forecast Metrics and Evaluation Functions.
"""

from typing import Dict, Any, Optional
import numpy as np


def compute_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Error."""
    return float(np.mean(np.abs(y_true - y_pred)))


def compute_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Root Mean Squared Error."""
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def compute_smape(y_true: np.ndarray, y_pred: np.ndarray, eps: float = 1e-12) -> float:
    """Symmetric Mean Absolute Percentage Error (0-100%)."""
    denom = np.abs(y_true) + np.abs(y_pred) + eps
    return float(np.mean(2.0 * np.abs(y_pred - y_true) / denom) * 100.0)


def compute_r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """R-squared Coefficient of Determination."""
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    if ss_tot == 0:
        return 0.0
    return float(1.0 - (ss_res / ss_tot))


def compute_mbe(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Bias Error (positive = overprediction, negative = underprediction)."""
    return float(np.mean(y_pred - y_true))


def compute_relative_improvement(mae_baseline: float, mae_model: float) -> float:
    """
    Computes relative improvement over baseline:
    relative_improvement = (MAE_baseline - MAE_model) / MAE_baseline
    Positive indicates improvement, negative indicates degradation.
    """
    if mae_baseline <= 0:
        return 0.0
    return float((mae_baseline - mae_model) / mae_baseline)


def evaluate_forecast_predictions(y_true: np.ndarray, y_pred: np.ndarray, mae_persistence: Optional[float] = None) -> Dict[str, float]:
    """
    Evaluates complete suite of forecast metrics.
    """
    # Remove any NaN or Inf pairs
    mask = np.isfinite(y_true) & np.isfinite(y_pred)
    y_t = y_true[mask]
    y_p = y_pred[mask]

    if len(y_t) == 0:
        return {
            "count": 0,
            "mae": float("nan"),
            "rmse": float("nan"),
            "smape": float("nan"),
            "r2": float("nan"),
            "mbe": float("nan"),
            "relative_improvement_vs_persistence": float("nan"),
        }

    mae = compute_mae(y_t, y_p)
    rmse = compute_rmse(y_t, y_p)
    smape = compute_smape(y_t, y_p)
    r2 = compute_r2(y_t, y_p)
    mbe = compute_mbe(y_t, y_p)

    rel_imp = compute_relative_improvement(mae_persistence, mae) if mae_persistence is not None else 0.0

    return {
        "count": len(y_t),
        "mae": mae,
        "rmse": rmse,
        "smape": smape,
        "r2": r2,
        "mbe": mbe,
        "relative_improvement_vs_persistence": rel_imp,
    }
