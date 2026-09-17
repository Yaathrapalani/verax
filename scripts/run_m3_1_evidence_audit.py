"""
FOUL-X M3.1 Baseline Evidence Completeness Audit Generator Script (Vectorized Engine).
Computes full exchanger validation and test evaluation tables, target scale analysis,
horizon evidence analysis, and outputs artifacts for M3.1.
"""

import sys
sys.path.insert(0, ".")
import json
from pathlib import Path
import numpy as np
import pandas as pd

from src.physics.state_estimator import PhysicsStateEstimator, EXCHANGER_MAPPING
from src.forecast.metrics import evaluate_forecast_predictions

RAW_DATA_PATH = Path("data/raw/heat_exchanger_fouling_dataset.csv")
M3_ARTIFACT_DIR = Path("artifacts/m3")

CANDIDATE_HORIZONS = [1, 6, 24, 72, 168]


def run_m3_1_audit():
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Raw dataset missing at {RAW_DATA_PATH}")

    df = pd.read_csv(RAW_DATA_PATH)
    estimator = PhysicsStateEstimator()
    ua_clean_refs = estimator.fit_baseline_from_dataframe(df, clean_window_hours=100)

    # Vectorized derivation of R_f_derived
    rf_series_dict = {}
    for tag, shell_name in EXCHANGER_MAPPING.items():
        m_t = df[f"{tag}_Crude_Tube_m_kg_s"]
        cp_t = df[f"{tag}_Crude_Tube_Cp_J_kgK"]
        t_t_in = df[f"{tag}_Crude_Tube_T_In_degC"]
        t_t_out = df[f"{tag}_Crude_Tube_T_Out_degC"]

        m_s = df[f"{tag}_{shell_name}_Shell_m_kg_s"]
        cp_s = df[f"{tag}_{shell_name}_Shell_Cp_J_kgK"]
        t_s_in = df[f"{tag}_{shell_name}_Shell_T_In_degC"]
        t_s_out = df[f"{tag}_{shell_name}_Shell_T_Out_degC"]

        Q_t = m_t * cp_t * (t_t_out - t_t_in)
        dt1 = t_s_in - t_t_out
        dt2 = t_s_out - t_t_in
        lmtd = (dt1 - dt2) / np.log(dt1 / dt2)
        UA = Q_t / lmtd
        ref_ua = ua_clean_refs[tag]
        Rf_derived = (1.0 / UA) - (1.0 / ref_ua)
        rf_series_dict[tag] = pd.Series(Rf_derived.values, index=df["Time_hr"], name=f"{tag}_R_f_derived")

    # 1. Target Scale Analysis
    target_scale_analysis = {}
    for tag, s in rf_series_dict.items():
        q25 = float(s.quantile(0.25))
        q75 = float(s.quantile(0.75))
        iqr = float(q75 - q25)
        std_val = float(s.std())
        range_val = float(s.max() - s.min())

        target_scale_analysis[tag] = {
            "exchanger_name": EXCHANGER_MAPPING[tag],
            "min": float(s.min()),
            "max": float(s.max()),
            "mean": float(s.mean()),
            "median": float(s.median()),
            "std": std_val,
            "q25": q25,
            "q75": q75,
            "q90": float(s.quantile(0.90)),
            "iqr": iqr,
            "range": range_val,
            "primary_target_scale_std": std_val,
            "secondary_target_scale_iqr": iqr,
        }

    M3_ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with open(M3_ARTIFACT_DIR / "target_scale_analysis.json", "w") as f:
        json.dump(target_scale_analysis, f, indent=2)

    # 2. Split Definitions
    val_mask = (df["Time_hr"] >= 44800) & (df["Time_hr"] <= 54399)
    test_mask = df["Time_hr"] >= 54400

    full_results = {}
    horizon_evidence = {}

    for tag, s in rf_series_dict.items():
        full_results[tag] = {"validation": {}, "test": {}}
        horizon_evidence[tag] = {}
        std_scale = target_scale_analysis[tag]["std"]

        # Fast vectorized baseline prediction vectors for the whole series
        # Persistence: P(t+h) = s(t)
        # Trend 24h: T(t+h) = s(t) + h * (s(t) - s(t-24))/24
        # Moving Average 24h: MA(t+h) = rolling_mean_24(t)
        slope_24h = (s - s.shift(24)) / 24.0
        ma_24h = s.rolling(24, min_periods=3).mean()

        splits = [("validation", val_mask), ("test", test_mask)]

        for split_name, split_mask in splits:
            for h in CANDIDATE_HORIZONS:
                # Target at t+h is s shifted backward by h
                y_true_full = s.shift(-h)

                # Persistence pred at t+h is s(t)
                y_pred_p_full = s

                # Trend 24h pred at t+h is s(t) + h * slope_24h(t)
                y_pred_t_full = s + (h * slope_24h)

                # Moving Average pred at t+h is ma_24h(t)
                y_pred_ma_full = ma_24h

                # Slice by split_mask
                y_true = y_true_full[split_mask].values
                y_p = y_pred_p_full[split_mask].values
                y_t = y_pred_t_full[split_mask].values
                y_ma = y_pred_ma_full[split_mask].values

                eval_p = evaluate_forecast_predictions(y_true, y_p)
                eval_t = evaluate_forecast_predictions(y_true, y_t, mae_persistence=eval_p["mae"])
                eval_ma = evaluate_forecast_predictions(y_true, y_ma, mae_persistence=eval_p["mae"])

                eval_p["normalized_mae_std"] = float(eval_p["mae"] / std_scale) if std_scale > 0 else float("nan")
                eval_t["normalized_mae_std"] = float(eval_t["mae"] / std_scale) if std_scale > 0 else float("nan")
                eval_ma["normalized_mae_std"] = float(eval_ma["mae"] / std_scale) if std_scale > 0 else float("nan")

                full_results[tag][split_name][f"{h}h"] = {
                    "Persistence": eval_p,
                    "RecentTrend_24h": eval_t,
                    "MovingAverage_24h": eval_ma,
                }

                if split_name == "validation":
                    target_changes = np.abs(s.shift(-h) - s).dropna()

                    horizon_evidence[tag][f"{h}h"] = {
                        "persistence_mae": eval_p["mae"],
                        "trend_mae": eval_t["mae"],
                        "moving_average_mae": eval_ma["mae"],
                        "target_autocorrelation": float(s.autocorr(lag=h)),
                        "target_variance": float(s.var()),
                        "target_mean_change_magnitude": float(target_changes.mean()),
                        "target_max_change_magnitude": float(target_changes.max()),
                        "persistence_error_to_target_scale_ratio": float(eval_p["mae"] / std_scale),
                        "horizon_suitability_classification": (
                            "HIGH_SUITABILITY" if h <= 6 else ("MODERATE_SUITABILITY" if h <= 24 else "HIGH_UNCERTAINTY_BASELINE_FAILURE")
                        ),
                    }

    with open(M3_ARTIFACT_DIR / "full_exchanger_baseline_results.json", "w") as f:
        json.dump(full_results, f, indent=2)

    with open(M3_ARTIFACT_DIR / "horizon_evidence.json", "w") as f:
        json.dump(horizon_evidence, f, indent=2)

    print("M3.1 Vectorized Evidence Audit completed cleanly.")


if __name__ == "__main__":
    run_m3_1_audit()
