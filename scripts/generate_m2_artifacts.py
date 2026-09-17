"""
Artifact Generator Script for FOUL-X M2 Physics State Estimator.
Generates artifacts/m2/sample_state.json and artifacts/m2/physics_state_profile.json.
"""

import sys
sys.path.insert(0, ".")
import json
from pathlib import Path
import numpy as np
import pandas as pd

from src.physics.state_estimator import PhysicsStateEstimator, EXCHANGER_MAPPING

RAW_DATA_PATH = Path("data/raw/heat_exchanger_fouling_dataset.csv")
SAMPLE_STATE_PATH = Path("artifacts/m2/sample_state.json")
PROFILE_STATE_PATH = Path("artifacts/m2/physics_state_profile.json")


def generate_m2_artifacts():
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Raw dataset missing at {RAW_DATA_PATH}")

    df = pd.read_csv(RAW_DATA_PATH)
    estimator = PhysicsStateEstimator()
    ua_clean_refs = estimator.fit_baseline_from_dataframe(df, clean_window_hours=100)

    # 1. Sample state generation (first timestep t=0 for all 5 exchangers)
    record_t0 = df.iloc[0].to_dict()
    sample_states = {}
    for tag in EXCHANGER_MAPPING.keys():
        state = estimator.process_record(record_t0, tag)
        sample_states[tag] = state.to_dict()

    SAMPLE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SAMPLE_STATE_PATH, "w") as f:
        json.dump(sample_states, f, indent=2)
    print(f"Sample state written to {SAMPLE_STATE_PATH}")

    # 2. Physics state profiling over all 64,000 timesteps
    exchanger_profiles = {}
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
        Q_s = m_s * cp_s * (t_s_in - t_s_out)

        dt1 = t_s_in - t_t_out
        dt2 = t_s_out - t_t_in
        lmtd = (dt1 - dt2) / (pd.Series(dt1 / dt2).apply(lambda x: np.log(x) if x > 0 else np.nan))
        UA = Q_t / lmtd
        ref_ua = ua_clean_refs[tag]
        Rf_derived = (1.0 / UA) - (1.0 / ref_ua)

        exchanger_profiles[tag] = {
            "exchanger_name": shell_name,
            "total_timesteps": len(df),
            "valid_state_count": int((UA > 0).sum()),
            "invalid_state_count": int((UA.isna() | (UA <= 0)).sum()),
            "ua_clean_reference_W_K": ref_ua,
            "q_tube_mean_MW": float(Q_t.mean() / 1e6),
            "q_shell_mean_MW": float(Q_s.mean() / 1e6),
            "thermal_balance_error_mean_pct": float(((Q_t - Q_s).abs() / pd.concat([Q_t, Q_s], axis=1).max(axis=1)).mean() * 100),
            "lmtd_mean_K": float(lmtd.mean()),
            "ua_mean_W_K": float(UA.mean()),
            "rf_derived_min": float(Rf_derived.min()),
            "rf_derived_max": float(Rf_derived.max()),
            "rf_derived_mean": float(Rf_derived.mean()),
        }

    profile_data = {
        "dataset_name": "Synthetic Shell-and-Tube Heat Exchanger Fouling",
        "total_observations": len(df),
        "exchanger_count": 5,
        "clean_baseline_window_hours": 100,
        "state_schema_version": "1.0",
        "calculation_version": "1.0",
        "exchanger_profiles": exchanger_profiles,
    }

    PROFILE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PROFILE_STATE_PATH, "w") as f:
        json.dump(profile_data, f, indent=2)
    print(f"Physics state profile written to {PROFILE_STATE_PATH}")


if __name__ == "__main__":
    generate_m2_artifacts()
