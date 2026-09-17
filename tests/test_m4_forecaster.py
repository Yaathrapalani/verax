import pytest
import numpy as np
import pandas as pd
from src.models.ridge_forecaster import RidgeFoulingForecaster
from src.models.schemas import TrainingConfig

def create_synthetic_features_and_target(n_rows=500):
    np.random.seed(42)
    X = pd.DataFrame({
        "feature_1": np.random.normal(0, 1, n_rows),
        "feature_2": np.random.normal(5, 2, n_rows),
        "feature_3": np.random.normal(10, 0.5, n_rows),
    })
    y = pd.Series(0.0001 + 0.00005 * X["feature_1"] + np.random.normal(0, 1e-6, n_rows))
    return X, y

def test_ridge_forecaster_fit_predict():
    X, y = create_synthetic_features_and_target(600)
    X_train, y_train = X.iloc[:350], y.iloc[:350]
    X_val, y_val = X.iloc[350:450], y.iloc[350:450]
    
    train_config = TrainingConfig(candidate_alphas=[0.1, 1.0, 10.0])
    
    forecaster = RidgeFoulingForecaster(alpha=1.0)
    best_alpha = forecaster.tune_alpha_on_validation(X_train, y_train, X_val, y_val, config=train_config)
    
    assert best_alpha in train_config.candidate_alphas
    assert forecaster.is_fitted
    
    preds = forecaster.predict(X_val)
    assert len(preds) == len(X_val)
    assert np.all(np.isfinite(preds))

def test_ridge_forecaster_determinism():
    X, y = create_synthetic_features_and_target(400)
    X_train, y_train = X.iloc[:250], y.iloc[:250]
    X_test = X.iloc[250:]
    
    forecaster1 = RidgeFoulingForecaster(alpha=2.5)
    forecaster1.fit(X_train, y_train)
    preds1 = forecaster1.predict(X_test)
    
    forecaster2 = RidgeFoulingForecaster(alpha=2.5)
    forecaster2.fit(X_train, y_train)
    preds2 = forecaster2.predict(X_test)
    
    np.testing.assert_array_equal(preds1, preds2)
