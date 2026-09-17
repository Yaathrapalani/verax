"""
Causal Feature Generator Engine for FOUL-X M4.0.
Strictly constructs historical features X(t) using observations <= t.
"""

from typing import List, Dict, Tuple
import pandas as pd
import numpy as np

from src.physics.state_estimator import PhysicsStateEstimator, EXCHANGER_MAPPING
from src.models.schemas import FeatureConfig


def extract_causal_features_for_exchanger(
    df: pd.DataFrame,
    tag: str,
    estimator: PhysicsStateEstimator,
    config: FeatureConfig = FeatureConfig()
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Constructs a causal feature DataFrame X(t) and derived target series Y_base(t) = R_f(t)
    for exchanger `tag` across all rows in `df`.
    
    STRICT CAUSALITY GUARANTEE:
    All features computed for index row i (timestamp t_i) use only observations at or before t_i.
    """
    shell_name = EXCHANGER_MAPPING[tag]
    ua_clean_ref = estimator.ua_clean_references.get(tag, 200000.0)

    # 1. Base thermodynamic calculations (vectorized for speed)
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
    lmtd = (dt1 - dt2) / np.log(dt1 / dt2)
    UA = Q_t / lmtd
    Rf_derived = (1.0 / UA) - (1.0 / ua_clean_ref)
    thermal_err = (Q_t - Q_s).abs() / np.maximum(Q_t, Q_s)

    # DataFrame to hold feature columns
    features = pd.DataFrame(index=df.index)

    # Current state features at time t
    features["Rf_derived_t"] = Rf_derived
    features["UA_t"] = UA
    features["LMTD_t"] = lmtd
    features["Q_tube_t"] = Q_t
    features["Q_shell_t"] = Q_s
    features["thermal_discrepancy_t"] = thermal_err

    # Operating variables at time t
    if config.include_operating_variables:
        features["Crude_API"] = df["Crude_API"]
        features["Crude_TAN"] = df["Crude_TAN"]
        features["Crude_Chlorides"] = df["Crude_Chlorides"]
        features["T_tube_in"] = t_t_in
        features["T_tube_out"] = t_t_out
        features["m_tube"] = m_t
        features["T_shell_in"] = t_s_in
        features["T_shell_out"] = t_s_out
        features["m_shell"] = m_s

    # Instantaneous delta and rolling slopes for R_f
    features["delta_Rf_1h"] = Rf_derived - Rf_derived.shift(1)
    features["rolling_Rf_slope_24h"] = (Rf_derived - Rf_derived.shift(24)) / 24.0

    # Causal window statistics for windows W in [6, 24, 72, 168]
    # Note: rolling(W) in pandas with default closed='right' includes timestamps [t-W+1 ... t]
    for W in config.window_sizes:
        roll = Rf_derived.rolling(window=W, min_periods=1)
        features[f"Rf_mean_{W}h"] = roll.mean()
        features[f"Rf_std_{W}h"] = roll.std().fillna(0.0)
        features[f"Rf_min_{W}h"] = roll.min()
        features[f"Rf_max_{W}h"] = roll.max()
        features[f"Rf_delta_{W}h"] = Rf_derived - Rf_derived.shift(W)
        features[f"Rf_slope_{W}h"] = (Rf_derived - Rf_derived.shift(W)) / float(W)

    # Backfill initial window NaNs with 0.0 for safety
    features = features.fillna(0.0)

    return features, pd.Series(Rf_derived.values, index=df.index, name="R_f_derived")
