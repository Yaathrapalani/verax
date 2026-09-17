"""
FOUL-X M1-B Primary Dataset Profiling and Audit Generator Script.
Reads data/raw/heat_exchanger_fouling_dataset.csv and generates artifacts/dataset_profile.json
and corresponding audit markdown files in data/.
"""

import json
import hashlib
from pathlib import Path
import pandas as pd

RAW_DATA_PATH = Path("data/raw/heat_exchanger_fouling_dataset.csv")
PROFILE_OUTPUT_PATH = Path("artifacts/dataset_profile.json")

COLUMN_CLASSIFICATIONS = {
    "Time_hr": "TIME",
    "Crude_API": "MEASURED_INPUT",
    "Crude_Chlorides": "MEASURED_INPUT",
    "Crude_TAN": "MEASURED_INPUT",
}

EXCHANGERS = [
    ("E01", "HeavyNaphtha"),
    ("E02", "Kero"),
    ("E03", "LightDiesel"),
    ("E04", "LVGO"),
    ("E05", "HeavyDiesel"),
]

for tag, name in EXCHANGERS:
    COLUMN_CLASSIFICATIONS[f"{tag}_Crude_Tube_Cp_J_kgK"] = "METADATA"
    COLUMN_CLASSIFICATIONS[f"{tag}_Crude_Tube_T_In_degC"] = "MEASURED_INPUT"
    COLUMN_CLASSIFICATIONS[f"{tag}_Crude_Tube_T_Out_degC"] = "MEASURED_INPUT"
    COLUMN_CLASSIFICATIONS[f"{tag}_Crude_Tube_m_kg_s"] = "MEASURED_INPUT"
    COLUMN_CLASSIFICATIONS[f"{tag}_Design_Duty_W"] = "METADATA"
    COLUMN_CLASSIFICATIONS[f"{tag}_{name}_Shell_Cp_J_kgK"] = "METADATA"
    COLUMN_CLASSIFICATIONS[f"{tag}_{name}_Shell_T_In_degC"] = "MEASURED_INPUT"
    COLUMN_CLASSIFICATIONS[f"{tag}_{name}_Shell_T_Out_degC"] = "MEASURED_INPUT"
    COLUMN_CLASSIFICATIONS[f"{tag}_{name}_Shell_m_kg_s"] = "MEASURED_INPUT"

    # Duplicated .1 columns
    COLUMN_CLASSIFICATIONS[f"{tag}_Crude_Tube_Cp_J_kgK.1"] = "DERIVED_INPUT"
    COLUMN_CLASSIFICATIONS[f"{tag}_Crude_Tube_T_In_degC.1"] = "DERIVED_INPUT"
    COLUMN_CLASSIFICATIONS[f"{tag}_Crude_Tube_T_Out_degC.1"] = "DERIVED_INPUT"
    COLUMN_CLASSIFICATIONS[f"{tag}_Crude_Tube_m_kg_s.1"] = "DERIVED_INPUT"


def compute_sha256(filepath: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def generate_profile():
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset missing at {RAW_DATA_PATH}")

    df = pd.read_csv(RAW_DATA_PATH)
    file_sha256 = compute_sha256(RAW_DATA_PATH)

    row_count, col_count = df.shape
    columns_info = {}

    duplicate_cols = [c for c in df.columns if c.endswith(".1")]
    constant_cols = [c for c in df.columns if df[c].nunique() == 1]
    suspicious_cols = duplicate_cols + [c for c in df.columns if "_True" in c]

    # Timestamp audit
    time_col = df["Time_hr"]
    time_monotonic = bool(time_col.is_monotonic_increasing)
    time_range = [float(time_col.min()), float(time_col.max())]
    time_diffs = time_col.diff().dropna()
    sampling_interval = float(time_diffs.median()) if not time_diffs.empty else None
    dup_timestamps = int(time_col.duplicated().sum())
    dup_rows = int(df.duplicated().sum())

    classified_cols = {}
    for col in df.columns:
        classification = COLUMN_CLASSIFICATIONS.get(col, "UNKNOWN")
        if "_True" in col:
            classification = "HIDDEN_GROUND_TRUTH"
        classified_cols[col] = classification

        columns_info[col] = {
            "dtype": str(df[col].dtype),
            "missing_count": int(df[col].isnull().sum()),
            "missing_pct": float(df[col].isnull().mean() * 100),
            "unique_count": int(df[col].nunique()),
            "classification": classification,
        }

    profile = {
        "dataset_name": "Synthetic Shell-and-Tube Heat Exchanger Fouling",
        "file_name": RAW_DATA_PATH.name,
        "sha256": file_sha256,
        "file_size_bytes": RAW_DATA_PATH.stat().st_size,
        "row_count": row_count,
        "column_count": col_count,
        "time_range_hours": time_range,
        "sampling_interval_hours": sampling_interval,
        "time_monotonic": time_monotonic,
        "duplicate_rows": dup_rows,
        "duplicate_timestamps": dup_timestamps,
        "exchanger_count": 5,
        "exchanger_ids": ["E01", "E02", "E03", "E04", "E05"],
        "constant_columns": constant_cols,
        "suspicious_columns": suspicious_cols,
        "columns": columns_info,
    }

    PROFILE_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PROFILE_OUTPUT_PATH, "w") as f:
        json.dump(profile, f, indent=2)

    print(f"Dataset profile written to {PROFILE_OUTPUT_PATH}")
    return profile


if __name__ == "__main__":
    generate_profile()
