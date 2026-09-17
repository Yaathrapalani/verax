"""
Ridge Regression Fouling Forecaster for FOUL-X M4.0.
Encapsulates scikit-learn Ridge regression + StandardScaler with training-only calibration.
"""

from typing import Dict, Any, Tuple, Optional, List
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge

from src.models.schemas import TrainingConfig
from src.forecast.metrics import evaluate_forecast_predictions


class RidgeFoulingForecaster:
    """
    Causal Ridge Regression Forecaster for R_f_derived(t+h).
    """

    def __init__(self, alpha: float = 1.0, random_state: int = 42):
        self.alpha = alpha
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.model = Ridge(alpha=self.alpha, random_state=self.random_state)
        self.is_fitted = False
        self.feature_names: List[str] = []

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series):
        """
        Fits StandardScaler and Ridge regression model ONLY on Training set split.
        """
        self.feature_names = list(X_train.columns)
        
        # Remove any invalid pairs
        mask = np.isfinite(y_train.values)
        X_tr = X_train.values[mask]
        y_tr = y_train.values[mask]

        X_scaled = self.scaler.fit_transform(X_tr)
        self.model.fit(X_scaled, y_tr)
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Generates predictions for feature matrix X.
        Uses previously fitted scaler (does NOT refit on test/validation data).
        """
        if not self.is_fitted:
            raise RuntimeError("Forecaster must be fitted before predicting!")
        
        X_scaled = self.scaler.transform(X.values)
        return self.model.predict(X_scaled)

    def tune_alpha_on_validation(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        config: TrainingConfig = TrainingConfig()
    ) -> float:
        """
        Selects best alpha hyperparameter using Validation set performance.
        Model is trained strictly on X_train/y_train for each alpha.
        """
        best_alpha = config.candidate_alphas[0]
        best_val_mae = float("inf")

        for alpha in config.candidate_alphas:
            scaler = StandardScaler()
            mask_tr = np.isfinite(y_train.values)
            X_tr_scaled = scaler.fit_transform(X_train.values[mask_tr])
            y_tr = y_train.values[mask_tr]

            model = Ridge(alpha=alpha, random_state=config.random_seed)
            model.fit(X_tr_scaled, y_tr)

            mask_val = np.isfinite(y_val.values)
            X_val_scaled = scaler.transform(X_val.values[mask_val])
            y_val_clean = y_val.values[mask_val]

            preds_val = model.predict(X_val_scaled)
            eval_res = evaluate_forecast_predictions(y_val_clean, preds_val)
            val_mae = eval_res["mae"]

            if val_mae < best_val_mae:
                best_val_mae = val_mae
                best_alpha = alpha

        self.alpha = best_alpha
        self.model = Ridge(alpha=self.alpha, random_state=config.random_seed)
        self.fit(X_train, y_train)
        return self.alpha
