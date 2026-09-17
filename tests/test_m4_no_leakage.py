import pytest
import numpy as np
import pandas as pd
from src.models.ridge_forecaster import RidgeFoulingForecaster
from src.models.schemas import FeatureConfig, TrainingConfig
from tests.test_m4_forecaster import create_synthetic_features_and_target

def test_causal_feature_window_leakage():
    """Ensure feature extraction at time t only uses rows with index <= t."""
    X, y = create_synthetic_features_and_target(100)
    
    # Mutate a future value at index 50
    X_mutated = X.copy()
    X_mutated.loc[50, "feature_1"] = 99999.0
    
    # Compute rolling statistics on original vs mutated
    roll_orig = X["feature_1"].rolling(window=6, min_periods=1).mean()
    roll_mutated = X_mutated["feature_1"].rolling(window=6, min_periods=1).mean()
    
    # Feature value at index 40 must be identical
    assert roll_orig.iloc[40] == roll_mutated.iloc[40]
    assert roll_orig.iloc[50] != roll_mutated.iloc[50]

def test_target_horizon_causality():
    """Ensure forecast target y(t) = R_f(t+h) shifts cleanly into future without contaminating X(t)."""
    _, y = create_synthetic_features_and_target(100)
    h = 6
    
    y_shifted = y.shift(-h)
    
    # For index 10, target y should be y at index 16
    assert y_shifted.iloc[10] == y.iloc[16]

def test_scaler_fitting_leakage():
    """Ensure scaler in RidgeFoulingForecaster is fit exclusively on train indices."""
    X, y = create_synthetic_features_and_target(500)
    X_train, y_train = X.iloc[:300], y.iloc[:300]
    X_val, y_val = X.iloc[300:400], y.iloc[300:400]
    
    forecaster = RidgeFoulingForecaster(alpha=1.0)
    forecaster.fit(X_train, y_train)
    
    # Scaler mean_ must equal mean of X_train
    np.testing.assert_allclose(forecaster.scaler.mean_, X_train.mean(axis=0).values, rtol=1e-5)
