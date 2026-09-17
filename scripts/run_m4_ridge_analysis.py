"""
FOUL-X M4.0 Ridge Regression Analysis & Artifact Generator Script (Instant Vectorized Engine).
Trains Ridge forecaster strictly on Training split, tunes alpha on Validation split,
evaluates on Validation & Test splits across all 5 exchangers and 3 horizons (1h, 6h, 24h).
"""

import sys
sys.path.insert(0, ".")
import json
import sklearn
import numpy as np
import pandas as pd
from pathlib import Path

from src.physics.state_estimator import PhysicsStateEstimator, EXCHANGER_MAPPING
from src.models.schemas import FeatureConfig, TrainingConfig
from src.models.features import extract_causal_features_for_exchanger
from src.models.ridge_forecaster import RidgeFoulingForecaster
from src.forecast.metrics import evaluate_forecast_predictions

RAW_DATA_PATH = Path("data/raw/heat_exchanger_fouling_dataset.csv")
M4_ARTIFACT_DIR = Path("artifacts/m4")
EVAL_HORIZONS = [1, 6, 24]


def run_m4_analysis():
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Raw dataset missing at {RAW_DATA_PATH}")

    df = pd.read_csv(RAW_DATA_PATH)
    estimator = PhysicsStateEstimator()
    estimator.fit_baseline_from_dataframe(df, clean_window_hours=100)

    # Train / Val / Test masks
    train_mask = df["Time_hr"] <= 44799.0
    val_mask = (df["Time_hr"] >= 44800.0) & (df["Time_hr"] <= 54399.0)
    test_mask = df["Time_hr"] >= 54400.0

    config = TrainingConfig()
    feat_config = FeatureConfig()

    m4_results = {}
    feature_schemas = {}

    for tag in EXCHANGER_MAPPING.keys():
        m4_results[tag] = {"validation": {}, "test": {}}

        # Extract causal feature matrix X and target R_f series
        X_df, rf_series = extract_causal_features_for_exchanger(df, tag, estimator, feat_config)
        feature_schemas[tag] = list(X_df.columns)

        std_scale = float(rf_series.std())

        for h in EVAL_HORIZONS:
            # Target Y(t+h) = R_f(t+h)
            y_target = rf_series.shift(-h)

            # Split X and y
            X_train, y_train = X_df[train_mask], y_target[train_mask]
            X_val, y_val = X_df[val_mask], y_target[val_mask]
            X_test, y_test = X_df[test_mask], y_target[test_mask]

            # Fit forecaster and tune alpha on validation set
            forecaster = RidgeFoulingForecaster(random_state=config.random_seed)
            best_alpha = forecaster.tune_alpha_on_validation(X_train, y_train, X_val, y_val, config)

            # Predict on Validation and Test sets
            preds_val = forecaster.predict(X_val)
            preds_test = forecaster.predict(X_test)

            # Vectorized Persistence predictions: R_hat(t+h) = R_f(t) evaluated on EXACT SAME target y(t+h)
            pers_preds_val = rf_series[val_mask].values
            pers_preds_test = rf_series[test_mask].values

            # Evaluate Validation metrics
            clean_val_mask = np.isfinite(y_val.values) & np.isfinite(preds_val) & np.isfinite(pers_preds_val)
            eval_p_val = evaluate_forecast_predictions(y_val.values[clean_val_mask], pers_preds_val[clean_val_mask])
            eval_r_val = evaluate_forecast_predictions(y_val.values[clean_val_mask], preds_val[clean_val_mask], mae_persistence=eval_p_val["mae"])
            eval_r_val["normalized_mae_std"] = float(eval_r_val["mae"] / std_scale) if std_scale > 0 else float("nan")
            eval_p_val["normalized_mae_std"] = float(eval_p_val["mae"] / std_scale) if std_scale > 0 else float("nan")

            # Evaluate Test metrics (reported separately, unused for model selection)
            clean_test_mask = np.isfinite(y_test.values) & np.isfinite(preds_test) & np.isfinite(pers_preds_test)
            eval_p_test = evaluate_forecast_predictions(y_test.values[clean_test_mask], pers_preds_test[clean_test_mask])
            eval_r_test = evaluate_forecast_predictions(y_test.values[clean_test_mask], preds_test[clean_test_mask], mae_persistence=eval_p_test["mae"])
            eval_r_test["normalized_mae_std"] = float(eval_r_test["mae"] / std_scale) if std_scale > 0 else float("nan")
            eval_p_test["normalized_mae_std"] = float(eval_p_test["mae"] / std_scale) if std_scale > 0 else float("nan")

            m4_results[tag]["validation"][f"{h}h"] = {
                "alpha": best_alpha,
                "Ridge": eval_r_val,
                "Persistence": eval_p_val,
                "absolute_mae_improvement": float(eval_p_val["mae"] - eval_r_val["mae"]),
                "relative_improvement_pct": eval_r_val["relative_improvement_vs_persistence"] * 100.0,
            }

            m4_results[tag]["test"][f"{h}h"] = {
                "alpha": best_alpha,
                "Ridge": eval_r_test,
                "Persistence": eval_p_test,
                "absolute_mae_improvement": float(eval_p_test["mae"] - eval_r_test["mae"]),
                "relative_improvement_pct": eval_r_test["relative_improvement_vs_persistence"] * 100.0,
            }

    M4_ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    with open(M4_ARTIFACT_DIR / "ridge_results.json", "w") as f:
        json.dump(m4_results, f, indent=2)

    with open(M4_ARTIFACT_DIR / "feature_schema.json", "w") as f:
        json.dump(feature_schemas, f, indent=2)

    with open(M4_ARTIFACT_DIR / "training_config.json", "w") as f:
        json.dump(config.model_dump(), f, indent=2)

    metadata = {
        "python_version": sys.version,
        "scikit_learn_version": sklearn.__version__,
        "dataset_sha256": "c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9",
        "state_schema_version": "1.0",
        "calculation_version": "1.0",
        "model_architecture": "StandardScaler + RidgeRegression",
        "candidate_horizons_hours": EVAL_HORIZONS,
        "evaluated_exchangers": list(EXCHANGER_MAPPING.keys()),
    }

    with open(M4_ARTIFACT_DIR / "model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print("M4.0 Ridge Regression Analysis completed cleanly.")


if __name__ == "__main__":
    run_m4_analysis()
