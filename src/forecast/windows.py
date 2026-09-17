"""
Causal Context Window Builders for FOUL-X.
"""

from typing import Tuple, List, Optional
import pandas as pd
import numpy as np


def get_causal_window(series: pd.Series, current_time: float, window_hours: int) -> Tuple[pd.Series, float, float]:
    """
    Extracts causal historical window of length window_hours up to current_time t.
    Window covers range [current_time - window_hours + 1, current_time].
    
    STRICT CAUSALITY GUARANTEE:
    Only timestamps <= current_time are returned.
    No observations > current_time participate in feature window.
    
    Returns:
        (window_slice, window_start_time, current_time)
    """
    if window_hours <= 0:
        raise ValueError("window_hours must be a positive integer!")
    
    start_time = current_time - window_hours + 1
    
    # Strictly filter for start_time <= index <= current_time
    mask = (series.index >= start_time) & (series.index <= current_time)
    window_slice = series[mask]
    
    return window_slice, start_time, current_time


def validate_window_causality(series: pd.Series, current_time: float, window_hours: int) -> bool:
    """
    Validates that no future timesteps (> current_time) are present in extracted window.
    """
    window_slice, start_t, end_t = get_causal_window(series, current_time, window_hours)
    if not window_slice.empty:
        max_t = window_slice.index.max()
        if max_t > current_time:
            return False
    return True
