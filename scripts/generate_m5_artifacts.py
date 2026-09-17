"""
FOUL-X M5.0 Reliability Artifact Generator Script.
Generates:
1. SUPPORTED_CASE (PASS result artifact)
2. DELIBERATELY_PERTURBED_UNSUPPORTED_CASE (ABSTAIN result artifact)
"""

import sys
sys.path.insert(0, ".")
import json
from pathlib import Path
import numpy as np
import pandas as pd

from src.physics.state_estimator import PhysicsStateEstimator, EXCHANGER_MAPPING
from src.models.schemas import FeatureConfig, TrainingConfig
from src.models.features import extract_causal_features_for_exchanger
from src.forecast.schemas import ForecastResult, ForecastStatus
from src.foulx.gate import (
    ReliabilityGateEvaluator,
    HistoricalRegimeSupportChecker,
    GateStatus,
)

RAW_DATA_PATH = Path("data/raw/heat_exchanger_fouling_dataset.csv")
M5_ARTIFACT_DIR = Path("artifacts/m5")


def generate_m5_artifacts():
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Raw dataset missing at {RAW_DATA_PATH}")

    df = pd.read_csv(RAW_DATA_PATH)
    estimator = PhysicsStateEstimator()
    estimator.fit_baseline_from_dataframe(df, clean_window_hours=100.0)

    train_mask = df["Time_hr"] <= 44799.0
    feat_config = FeatureConfig()

    tag = "E01"
    shell_name = EXCHANGER_MAPPING[tag]

    # Extract features for E01
    X_df, rf_series = extract_causal_features_for_exchanger(df, tag, estimator, feat_config)
    X_train = X_df[train_mask]

    # Fit Historical Regime Support Checker strictly on Training split
    regime_checker = HistoricalRegimeSupportChecker(z_score_threshold=4.0)
    regime_checker.fit_on_training_data(X_train)

    evaluator = ReliabilityGateEvaluator(regime_checker=regime_checker)

    # 1. SUPPORTED_CASE (Validation row t = 45,000h)
    target_idx = df.index[df["Time_hr"] == 45000.0][0]
    raw_supported = df.iloc[target_idx].to_dict()
    state_supported = estimator.process_record(raw_supported, tag)
    feat_vec_supported = X_df.iloc[target_idx]

    forecast_supported = ForecastResult(
        exchanger_id=tag,
        timestamp=45000.0,
        horizon_hours=24,
        prediction=float(rf_series.iloc[target_idx]),
        input_window_start=44976.0,
        input_window_end=45000.0,
        status=ForecastStatus.SUCCESS,
        method="RidgeRegression",
    )

    required_fields = [
        f"{tag}_Crude_Tube_T_In_degC",
        f"{tag}_Crude_Tube_T_Out_degC",
        f"{tag}_{shell_name}_Shell_T_In_degC",
        f"{tag}_{shell_name}_Shell_T_Out_degC",
        f"{tag}_Crude_Tube_m_kg_s",
        f"{tag}_{shell_name}_Shell_m_kg_s",
    ]

    res_supported = evaluator.evaluate_reliability(
        raw_record=raw_supported,
        required_fields=required_fields,
        tag=tag,
        shell_name=shell_name,
        canonical_state=state_supported,
        forecast_result=forecast_supported,
        feature_vector=feat_vec_supported,
    )

    # 2. DELIBERATELY_PERTURBED_UNSUPPORTED_CASE
    # Synthetic perturbation: perturb Crude_API to 99.0 (OOD) and inject NaN into mass flow
    raw_perturbed = raw_supported.copy()
    raw_perturbed[f"{tag}_Crude_Tube_T_In_degC"] = float("nan") # Triggers SENSOR_INVALID & M2 Physics Inconsistency
    raw_perturbed.pop(f"{tag}_Crude_Tube_m_kg_s") # Triggers DATA_INCOMPLETE
    
    state_perturbed = estimator.process_record(raw_supported, tag)
    
    # Perturb feature vector Z-score to trigger REGIME_OOD (> 4 std)
    feat_vec_perturbed = feat_vec_supported.copy()
    feat_vec_perturbed["Rf_derived_t"] = 99.0 # Synthetic OOD perturbation for gate validation

    forecast_perturbed = ForecastResult(
        exchanger_id=tag,
        timestamp=45000.0,
        horizon_hours=24,
        prediction=None,
        input_window_start=44976.0,
        input_window_end=45000.0,
        status=ForecastStatus.INVALID_CURRENT_STATE,
        method="RidgeRegression",
    )

    res_perturbed = evaluator.evaluate_reliability(
        raw_record=raw_perturbed,
        required_fields=required_fields,
        tag=tag,
        shell_name=shell_name,
        canonical_state=state_perturbed,
        forecast_result=forecast_perturbed,
        feature_vector=feat_vec_perturbed,
    )

    M5_ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    with open(M5_ARTIFACT_DIR / "supported_case.json", "w") as f:
        json.dump(res_supported.to_dict(), f, indent=2)

    with open(M5_ARTIFACT_DIR / "deliberately_perturbed_unsupported_case.json", "w") as f:
        json.dump(res_perturbed.to_dict(), f, indent=2)

    print("M5.0 Reliability Gate Artifacts generated cleanly.")


if __name__ == "__main__":
    generate_m5_artifacts()
