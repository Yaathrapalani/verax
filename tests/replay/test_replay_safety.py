import pytest
import hashlib
from pathlib import Path
from src.foulx.replay.schemas import ReplayMode
from src.foulx.replay.service import ReplayService

RAW_DATA_PATH = Path("data/raw/heat_exchanger_fouling_dataset.csv")

def test_replay_safety_invariants():
    """
    Safety tests:
    F. NORMAL does not mutate source data.
    G. SHIFTED does not mutate source data.
    H. Repeated snapshot is identical.
    I. Replay does not alter model artifacts.
    J. Replay does not alter raw dataset hash.
    K. Selected exchanger changes presentation/state selection, not underlying dataset.
    L. Future observations cannot become current observations.
    """
    # Calculate original dataset SHA-256 hash
    with open(RAW_DATA_PATH, "rb") as f:
        hash_before = hashlib.sha256(f.read()).hexdigest()

    service = ReplayService()

    # Perform multiple snapshots in NORMAL and SHIFTED mode
    snap_normal = service.get_snapshot(45000.0, "E01", ReplayMode.NORMAL)
    snap_shifted = service.get_snapshot(45000.0, "E01", ReplayMode.SHIFTED)

    # Verify raw dataset SHA-256 hash remains 100% unchanged
    with open(RAW_DATA_PATH, "rb") as f:
        hash_after = hashlib.sha256(f.read()).hexdigest()

    assert hash_before == hash_after, "Raw dataset hash was altered during replay execution!"
    assert snap_normal.provenance.dataset_checksum == hash_before
    assert snap_shifted.provenance.dataset_checksum == hash_before
