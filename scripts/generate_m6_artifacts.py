"""
FOUL-X M6.0 Decision Artifact Generator Script.
Generates:
1. operate_case.json
2. cleaning_review_case.json
3. abstain_case.json
"""

import sys
sys.path.insert(0, ".")
import json
from pathlib import Path
import numpy as np
import pandas as pd

from src.physics.state_estimator import PhysicsStateEstimator, EXCHANGER_MAPPING
from src.models.schemas import FeatureConfig
from src.models.features import extract_causal_features_for_exchanger
from src.forecast.schemas import ForecastResult, ForecastStatus
from src.foulx.gate import (
    ReliabilityGateEvaluator,
    HistoricalRegimeSupportChecker,
    GateStatus,
)
from src.foulx.decision import (
    DecisionEngineEvaluator,
    DecisionThresholdConfig,
)

RAW_DATA_PATH = Path("data/raw/heat_exchanger_fouling_dataset.csv")
M6_ARTIFACT_DIR = Path("artifacts/m6")


def generate_m6_artifacts():
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Raw dataset missing at {RAW_DATA_PATH}")

    df = pd.read_csv(RAW_DATA_PATH)
    estimator = PhysicsStateEstimator()
    estimator.fit_baseline_from_dataframe(df, clean_window_hours=100.0)

    train_mask = df["Time_hr"] <= 44799.0
    feat_config = FeatureConfig()

    tag = "E01"
    shell_name = EXCHANGER_MAPPING[tag]

    # Extract features & fit regime support checker on Train split
    X_df, rf_series = extract_causal_features_for_exchanger(df, tag, estimator, feat_config)
    X_train = X_df[train_mask]

    regime_checker = HistoricalRegimeSupportChecker(z_score_threshold=4.0)
    regime_checker.fit_on_training_data(X_train)

    gate_evaluator = ReliabilityGateEvaluator(regime_checker=regime_checker)
    decision_evaluator = DecisionEngineEvaluator()

    # Base target Validation row t = 45,000h
    target_idx = df.index[df["Time_hr"] == 45000.0][0]
    raw_record = df.iloc[target_idx].to_dict()
    state_valid = estimator.process_record(raw_record, tag)
    feat_vec = X_df.iloc[target_idx]

    required_fields = [
        f"{tag}_Crude_Tube_T_In_degC",
        f"{tag}_Crude_Tube_T_Out_degC",
        f"{tag}_{shell_name}_Shell_T_In_degC",
        f"{tag}_{shell_name}_Shell_T_Out_degC",
        f"{tag}_Crude_Tube_m_kg_s",
        f"{tag}_{shell_name}_Shell_m_kg_s",
    ]

    forecast_base = ForecastResult(
        exchanger_id=tag,
        timestamp=45000.0,
        horizon_hours=24,
        prediction=float(rf_series.iloc[target_idx]),
        input_window_start=44976.0,
        input_window_end=45000.0,
        status=ForecastStatus.SUCCESS,
        method="RidgeRegression",
    )

    rel_pass = gate_evaluator.evaluate_reliability(
        raw_record=raw_record,
        required_fields=required_fields,
        tag=tag,
        shell_name=shell_name,
        canonical_state=state_valid,
        forecast_result=forecast_base,
        feature_vector=feat_vec,
    )

    # 1. OPERATE CASE (PASS + threshold 1.5e-7 not reached)
    cfg_operate = DecisionThresholdConfig(rf_threshold=1.5e-7, planning_horizon_hours=24, exchanger_id=tag)
    forecasts_operate = [
        ForecastResult(exchanger_id=tag, timestamp=45000.0, horizon_hours=1, prediction=7.5e-8, input_window_start=44999.0, input_window_end=45000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression"),
        ForecastResult(exchanger_id=tag, timestamp=45000.0, horizon_hours=6, prediction=8.5e-8, input_window_start=44994.0, input_window_end=45000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression"),
        ForecastResult(exchanger_id=tag, timestamp=45000.0, horizon_hours=24, prediction=1.1e-7, input_window_start=44976.0, input_window_end=45000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression"),
    ]
    res_operate = decision_evaluator.evaluate_decision(rel_pass, state_valid, forecasts_operate, cfg_operate)

    # 2. CLEANING REVIEW CASE (PASS + threshold 1.5e-7 reached at horizon 24h)
    cfg_review = DecisionThresholdConfig(rf_threshold=1.5e-7, planning_horizon_hours=24, exchanger_id=tag)
    forecasts_review = [
        ForecastResult(exchanger_id=tag, timestamp=45000.0, horizon_hours=1, prediction=7.5e-8, input_window_start=44999.0, input_window_end=45000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression"),
        ForecastResult(exchanger_id=tag, timestamp=45000.0, horizon_hours=6, prediction=1.2e-7, input_window_start=44994.0, input_window_end=45000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression"),
        ForecastResult(exchanger_id=tag, timestamp=45000.0, horizon_hours=24, prediction=1.8e-7, input_window_start=44976.0, input_window_end=45000.0, status=ForecastStatus.SUCCESS, method="RidgeRegression"),
    ]
    res_review = decision_evaluator.evaluate_decision(rel_pass, state_valid, forecasts_review, cfg_review)
    res_review.evidence["fixture_note"] = "synthetic decision fixture for M6 validation"

    # 3. ABSTAIN CASE (M5 ABSTAIN -> M6 ABSTAIN)
    raw_perturbed = raw_record.copy()
    raw_perturbed[f"{tag}_Crude_Tube_T_In_degC"] = float("nan")
    raw_perturbed.pop(f"{tag}_Crude_Tube_m_kg_s")
    
    state_perturbed = estimator.process_record(raw_record, tag)
    feat_vec_perturbed = feat_vec.copy()
    feat_vec_perturbed["Rf_derived_t"] = 99.0

    rel_abstain = gate_evaluator.evaluate_reliability(
        raw_record=raw_perturbed,
        required_fields=required_fields,
        tag=tag,
        shell_name=shell_name,
        canonical_state=state_perturbed,
        forecast_result=forecast_base,
        feature_vector=feat_vec_perturbed,
    )

    res_abstain = decision_evaluator.evaluate_decision(rel_abstain, state_valid, forecasts_operate, cfg_operate)

    M6_ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    with open(M6_ARTIFACT_DIR / "operate_case.json", "w") as f:
        json.dump(res_operate.to_dict(), f, indent=2)

    with open(M6_ARTIFACT_DIR / "cleaning_review_case.json", "w") as f:
        json.dump(res_review.to_dict(), f, indent=2)

    with open(M6_ARTIFACT_DIR / "abstain_case.json", "w") as f:
        json.dump(res_abstain.to_dict(), f, indent=2)

    print("M6.0 Decision Engine Artifacts generated cleanly.")


if __name__ == "__main__":
    generate_m6_artifacts()
