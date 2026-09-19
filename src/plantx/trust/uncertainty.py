"""Uncertainty quantification models and calibration routines for Stage 7."""

from typing import Dict, Any, Tuple, Optional, List
import numpy as np
import pandas as pd
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

from src.plantx.trust.schemas import PredictionInterval, CalibrationReport


class GaussianProcessFoulingChallenger:
    """Gaussian Process Regression challenger model providing explicit predictive uncertainty."""

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        kernel = 1.0 * RBF(length_scale=1.0) + WhiteKernel(noise_level=1e-4)
        self.gpr = GaussianProcessRegressor(kernel=kernel, random_state=random_state, n_restarts_optimizer=2)
        self.is_fitted = False

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series):
        mask = np.isfinite(y_train.values)
        X_tr = X_train.values[mask]
        y_tr = y_train.values[mask]
        # Subsample for computational speed if large
        if len(X_tr) > 1000:
            idx = np.random.choice(len(X_tr), 1000, replace=False)
            X_tr = X_tr[idx]
            y_tr = y_tr[idx]
        self.gpr.fit(X_tr, y_tr)
        self.is_fitted = True
        return self

    def predict_with_uncertainty(
        self,
        X: pd.DataFrame,
        confidence_level: float = 0.95,
    ) -> Tuple[np.ndarray, np.ndarray, List[PredictionInterval]]:
        if not self.is_fitted:
            raise RuntimeError("GPR model must be fitted prior to prediction.")
        
        y_mean, y_std = self.gpr.predict(X.values, return_std=True)
        # z-multiplier for 95% nominal level ~ 1.96
        z_val = 1.96 if abs(confidence_level - 0.95) < 1e-3 else 1.96
        
        intervals = []
        for mean, std in zip(y_mean, y_std):
            lower = float(mean - z_val * std)
            upper = float(mean + z_val * std)
            intervals.append(
                PredictionInterval(
                    lower_bound=lower,
                    upper_bound=upper,
                    nominal_level=confidence_level,
                    method="GaussianProcessRegressor",
                    model_version="1.0.0",
                    calibration_status="UNCALIBRATED",
                )
            )
        return y_mean, y_std, intervals


class EmpiricalCalibrationEvaluator:
    """Evaluates empirical coverage and interval calibration metrics strictly without tuning on test set."""

    @staticmethod
    def evaluate_calibration(
        y_true: np.ndarray,
        intervals: List[PredictionInterval],
        nominal_level: float = 0.95,
    ) -> CalibrationReport:
        if len(y_true) == 0 or len(intervals) == 0:
            return CalibrationReport(
                nominal_level=nominal_level,
                empirical_coverage=0.0,
                coverage_error=1.0,
                mean_interval_width=0.0,
                sample_count=0,
                calibration_status="UNAVAILABLE",
            )

        inside_count = 0
        total_width = 0.0

        for y, inv in zip(y_true, intervals):
            if inv.lower_bound <= y <= inv.upper_bound:
                inside_count += 1
            total_width += (inv.upper_bound - inv.lower_bound)

        emp_coverage = float(inside_count / len(y_true))
        cov_error = float(abs(emp_coverage - nominal_level))
        mean_width = float(total_width / len(y_true))
        cal_status = "CALIBRATED" if cov_error <= 0.05 else "MISCALIBRATED"

        return CalibrationReport(
            nominal_level=nominal_level,
            empirical_coverage=emp_coverage,
            coverage_error=cov_error,
            mean_interval_width=mean_width,
            sample_count=len(y_true),
            calibration_status=cal_status,
        )
