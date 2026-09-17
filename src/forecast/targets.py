"""
Target construction utilities for FOUL-X forecasting.
"""

from typing import Dict, Optional, List
import pandas as pd
import numpy as np


def construct_target_series(rf_series: pd.Series, horizon_hours: int) -> pd.Series:
    """
    Constructs future target Y(t+h) = R_f_derived(t+h) by shifting series backward by horizon_hours.
    Target at index t is the value of R_f_derived at index t + horizon_hours.
    """
    if horizon_hours <= 0:
        raise ValueError("horizon_hours must be positive integer!")
    
    target_series = rf_series.shift(-horizon_hours)
    target_series.name = f"R_f_derived_t_plus_{horizon_hours}h"
    return target_series


def extract_target_value(rf_series: pd.Series, current_time: float, horizon_hours: int) -> Optional[float]:
    """
    Extracts future target R_f_derived(t + horizon_hours) for a given current_time t.
    """
    target_time = current_time + horizon_hours
    matching = rf_series[rf_series.index == target_time]
    if len(matching) == 0:
        return None
    val = float(matching.iloc[0])
    return val if np.isfinite(val) else None
