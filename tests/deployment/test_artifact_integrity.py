import pytest
import hashlib
from pathlib import Path

RAW_DATA_PATH = Path("data/raw/heat_exchanger_fouling_dataset.csv")
REQUIRED_ARTIFACT_DIRS = [
    Path("artifacts/m2"),
    Path("artifacts/m4"),
    Path("artifacts/m5"),
    Path("artifacts/m6"),
    Path("artifacts/m7"),
    Path("artifacts/m9"),
    Path("artifacts/m10"),
]


def test_raw_dataset_hash_integrity():
    assert RAW_DATA_PATH.exists()
    with open(RAW_DATA_PATH, "rb") as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()
    expected_hash = "c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9"
    assert actual_hash == expected_hash, f"Dataset SHA-256 hash mismatch! Found {actual_hash}"


def test_required_artifacts_exist():
    for artifact_dir in REQUIRED_ARTIFACT_DIRS:
        assert artifact_dir.exists(), f"Missing required artifact directory: {artifact_dir}"
        assert len(list(artifact_dir.glob("*.json"))) > 0, f"No JSON artifacts in {artifact_dir}"
