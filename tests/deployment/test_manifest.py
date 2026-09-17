import pytest
import json
from pathlib import Path
from src.foulx.replay.resolver import HistoricalStateResolver

MANIFEST_PATH = Path("artifacts/m10/deployment_manifest.json")


def test_deployment_manifest_structure():
    assert MANIFEST_PATH.exists(), "deployment_manifest.json missing!"
    with open(MANIFEST_PATH) as f:
        data = json.load(f)

    assert data["project"] == "FOUL-X"
    assert data["dataset_checksum"] == "c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9"
    assert data["dataset_time_range_hours"] == [0.0, 63999.0]
    assert data["m10_deployment_status"] == "VALIDATED_REPRODUCIBLE"
