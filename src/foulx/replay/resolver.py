"""
Historical Data & State Resolver for FOUL-X M9.0 Replay Engine.

Retrieves exact historical observations at t <= timestamp from dataset without future leakage.
"""

from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
import pandas as pd

RAW_DATA_PATH = Path("data/raw/heat_exchanger_fouling_dataset.csv")

VALID_EXCHANGERS = {
    "E01": "HeavyNaphtha",
    "E02": "Kero",
    "E03": "LightDiesel",
    "E04": "LVGO",
    "E05": "HeavyDiesel",
}


class HistoricalStateResolver:
    """
    Resolves historical raw data records and dataset slices for replay.
    Guarantees that observations returned for timestamp t contain ONLY data where Time_hr <= t.
    """

    def __init__(self, data_path: Path = RAW_DATA_PATH):
        self.data_path = data_path
        self._df: Optional[pd.DataFrame] = None

    def _get_df(self) -> pd.DataFrame:
        if self._df is None:
            if not self.data_path.exists():
                raise FileNotFoundError(f"Raw dataset not found at {self.data_path}")
            self._df = pd.read_csv(self.data_path)
        return self._df

    def get_min_max_timestamps(self) -> Tuple[float, float]:
        df = self._get_df()
        return float(df["Time_hr"].min()), float(df["Time_hr"].max())

    def resolve_raw_record(self, timestamp: float) -> Tuple[Dict[str, Any], int]:
        """
        Retrieves raw record dictionary at exact timestamp t.
        Returns (record_dict, index).
        Raises ValueError if timestamp is out of range or not found.
        """
        df = self._get_df()
        t_val = float(timestamp)

        # Exact row match
        matched = df[df["Time_hr"] == t_val]
        if matched.empty:
            raise ValueError(f"Timestamp {t_val} not found in historical dataset!")

        idx = matched.index[0]
        record = matched.iloc[0].to_dict()
        return record, int(idx)

    def resolve_causal_history(self, timestamp: float, window_hours: int = 168) -> pd.DataFrame:
        """
        Retrieves DataFrame slice up to and including timestamp t (Time_hr <= t).
        Guarantees ZERO future data leakage.
        """
        df = self._get_df()
        t_val = float(timestamp)
        return df[(df["Time_hr"] <= t_val) & (df["Time_hr"] >= t_val - window_hours)].copy()
