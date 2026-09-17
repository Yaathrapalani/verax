"""
FOUL-X M3 Baseline Forecasting & Target Dynamics Analysis Script (Fast Vectorized Engine).
Generates baseline results, horizon analysis, target dynamics JSONs, and visual plots.
"""

import sys
sys.path.insert(0, ".")
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.physics.state_estimator import PhysicsStateEstimator, EXCHANGER_MAPPING
from src.forecast.baselines import PersistenceBaseline, RecentTrendBaseline, MovingAverageBaseline
from src.forecast.metrics import evaluate_forecast_predictions

RAW_DATA_PATH = Path("data/raw/heat_exchanger_fouling_dataset.csv")
M3_ARTIFACT_DIR = Path("artifacts/m3")
PLOTS_DIR = M3_ARTIFACT_DIR / "plots"

CANDIDATE_HORIZONS = [1, 6, 24, 72, 168]


def run_m3_analysis():
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

    # 1. Target Dynamics Analysis
    target_dynamics = {}
    for tag, s in rf_series_dict.items():
        diff1 = s.diff().dropna()
        autocorr_1 = float(s.autocorr(lag=1))
        autocorr_24 = float(s.autocorr(lag=24))
        autocorr_168 = float(s.autocorr(lag=168))

        target_dynamics[tag] = {
            "mean": float(s.mean()),
            "std": float(s.std()),
            "var": float(s.var()),
            "min": float(s.min()),
            "max": float(s.max()),
            "first_diff_mean": float(diff1.mean()),
            "first_diff_std": float(diff1.std()),
            "degradation_rate_per_hour_mean": float(diff1.mean()),
            "autocorrelation": {
                "lag_1h": autocorr_1,
                "lag_24h": autocorr_24,
                "lag_168h": autocorr_168,
            },
        }

    M3_ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with open(M3_ARTIFACT_DIR / "target_dynamics.json", "w") as f:
        json.dump(target_dynamics, f, indent=2)

    # 2. Evaluate Baselines per Exchanger, Horizon, and Split
    val_mask = (df["Time_hr"] >= 44800) & (df["Time_hr"] <= 54399)
    val_df = df[val_mask]

    persistence = PersistenceBaseline()
    trend_24h = RecentTrendBaseline(trend_window_hours=24)
    ma_24h = MovingAverageBaseline(ma_window_hours=24)

    baseline_results = {}
    horizon_analysis = {}

    for tag, s in rf_series_dict.items():
        baseline_results[tag] = {}
        horizon_analysis[tag] = {}

        # Subsample validation timestamps for fast evaluation (every 10th hour = ~960 samples per exchanger)
        eval_times = val_df["Time_hr"].values[::10]

        for h in CANDIDATE_HORIZONS:
            y_true_list = []
            y_pred_p_list = []
            y_pred_t_list = []
            y_pred_ma_list = []

            for t in eval_times:
                t_future = t + h
                if t_future not in s.index:
                    continue
                y_true_val = float(s.loc[t_future])
                if not np.isfinite(y_true_val):
                    continue

                res_p = persistence.predict(s, t, h, tag)
                res_t = trend_24h.predict(s, t, h, tag)
                res_ma = ma_24h.predict(s, t, h, tag)

                if res_p.status.value == "SUCCESS" and res_t.status.value == "SUCCESS" and res_ma.status.value == "SUCCESS":
                    y_true_list.append(y_true_val)
                    y_pred_p_list.append(res_p.prediction)
                    y_pred_t_list.append(res_t.prediction)
                    y_pred_ma_list.append(res_ma.prediction)

            y_true = np.array(y_true_list)
            y_p = np.array(y_pred_p_list)
            y_t = np.array(y_pred_t_list)
            y_ma = np.array(y_pred_ma_list)

            eval_p = evaluate_forecast_predictions(y_true, y_p)
            eval_t = evaluate_forecast_predictions(y_true, y_t, mae_persistence=eval_p["mae"])
            eval_ma = evaluate_forecast_predictions(y_true, y_ma, mae_persistence=eval_p["mae"])

            baseline_results[tag][f"{h}h"] = {
                "Persistence": eval_p,
                "RecentTrend_24h": eval_t,
                "MovingAverage_24h": eval_ma,
            }

            horizon_analysis[tag][f"{h}h"] = {
                "mae_persistence": eval_p["mae"],
                "mae_trend": eval_t["mae"],
                "mae_ma": eval_ma["mae"],
                "relative_improvement_trend_pct": eval_t["relative_improvement_vs_persistence"] * 100.0,
                "relative_improvement_ma_pct": eval_ma["relative_improvement_vs_persistence"] * 100.0,
                "r2_persistence": eval_p["r2"],
                "r2_trend": eval_t["r2"],
            }

    with open(M3_ARTIFACT_DIR / "baseline_results.json", "w") as f:
        json.dump(baseline_results, f, indent=2)

    with open(M3_ARTIFACT_DIR / "horizon_analysis.json", "w") as f:
        json.dump(horizon_analysis, f, indent=2)

    # 3. Generate Visual Plot Artifacts
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    # Plot 1: R_f Trajectories by Exchanger
    plt.figure(figsize=(12, 6))
    for tag, s in rf_series_dict.items():
        plt.plot(s.index[:2000], s.values[:2000], label=f"{tag} ({EXCHANGER_MAPPING[tag]})")
    plt.title("FOUL-X M3 — Derived Fouling Resistance Proxy R_f (First 2000h)")
    plt.xlabel("Time (hours)")
    plt.ylabel("R_f_derived (m²·K/W)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "rf_trajectories.png", dpi=300)
    plt.close()

    # Plot 2: Actual vs Persistence (E01, 24h horizon)
    sample_s = rf_series_dict["E01"]
    val_t_sub = val_df["Time_hr"].values[:300]
    act_vals = [sample_s.get(t + 24, np.nan) for t in val_t_sub]
    pers_vals = [persistence.predict(sample_s, t, 24, "E01").prediction for t in val_t_sub]

    plt.figure(figsize=(12, 6))
    plt.plot(val_t_sub + 24, act_vals, label="Actual R_f(t+24h)", color="black")
    plt.plot(val_t_sub + 24, pers_vals, label="Persistence R_hat(t+24h)", color="blue", linestyle="--")
    plt.title("E01 — Actual vs Persistence Baseline (Horizon = 24h)")
    plt.xlabel("Time (hours)")
    plt.ylabel("R_f_derived (m²·K/W)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "actual_vs_persistence.png", dpi=300)
    plt.close()

    # Plot 3: Actual vs Trend Baseline (E01, 24h horizon)
    trend_vals = [trend_24h.predict(sample_s, t, 24, "E01").prediction for t in val_t_sub]

    plt.figure(figsize=(12, 6))
    plt.plot(val_t_sub + 24, act_vals, label="Actual R_f(t+24h)", color="black")
    plt.plot(val_t_sub + 24, trend_vals, label="RecentTrend(24h) R_hat(t+24h)", color="crimson", linestyle="--")
    plt.title("E01 — Actual vs Recent-Trend Baseline (Horizon = 24h)")
    plt.xlabel("Time (hours)")
    plt.ylabel("R_f_derived (m²·K/W)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "actual_vs_trend.png", dpi=300)
    plt.close()

    # Plot 4: Forecast Error by Horizon (MAE across horizons for E01)
    maes_p = [horizon_analysis["E01"][f"{h}h"]["mae_persistence"] for h in CANDIDATE_HORIZONS]
    maes_t = [horizon_analysis["E01"][f"{h}h"]["mae_trend"] for h in CANDIDATE_HORIZONS]

    plt.figure(figsize=(10, 5))
    plt.plot(CANDIDATE_HORIZONS, maes_p, marker="o", label="Persistence MAE", color="blue")
    plt.plot(CANDIDATE_HORIZONS, maes_t, marker="s", label="RecentTrend(24h) MAE", color="crimson")
    plt.title("E01 — Forecast Error (MAE) Degradation by Horizon")
    plt.xlabel("Horizon h (hours)")
    plt.ylabel("MAE (m²·K/W)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "error_by_horizon.png", dpi=300)
    plt.close()

    # Plot 5: Residual Distribution (E01, 24h horizon)
    res_p = np.array(pers_vals) - np.array(act_vals)
    res_t = np.array(trend_vals) - np.array(act_vals)

    plt.figure(figsize=(10, 5))
    plt.hist(res_p, bins=30, alpha=0.5, label="Persistence Residuals", color="blue")
    plt.hist(res_t, bins=30, alpha=0.5, label="RecentTrend Residuals", color="crimson")
    plt.title("E01 — Residual Distribution (Horizon = 24h)")
    plt.xlabel("Forecast Error (Residuals)")
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "residual_distributions.png", dpi=300)
    plt.close()

    print("M3 Analysis completed and artifacts generated.")


if __name__ == "__main__":
    run_m3_analysis()
