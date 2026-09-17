import pytest
from src.foulx.replay.schemas import ReplayMode
from src.foulx.replay.service import ReplayService

def test_replay_boundaries_and_split_timestamps():
    """
    Tests replay execution at exact split boundary timestamps:
    - Train end: 44799.0
    - Val start: 44800.0
    - Val end: 54399.0
    - Test start: 54400.0
    - Test end: 63999.0
    """
    service = ReplayService()

    boundary_timestamps = [0.0, 44799.0, 44800.0, 54399.0, 54400.0, 63999.0]
    for t in boundary_timestamps:
        snap = service.get_snapshot(t, "E01", ReplayMode.NORMAL)
        assert snap.timestamp == t
        assert snap.physics_state.timestamp == t

def test_out_of_range_boundaries():
    service = ReplayService()
    
    # Seek before start
    with pytest.raises(ValueError):
        service.seek(-1.0)

    # Seek after end
    with pytest.raises(ValueError):
        service.seek(64000.0)

    # Invalid exchanger
    with pytest.raises(ValueError, match="Unknown exchanger_id"):
        service.get_snapshot(45000.0, "E99", ReplayMode.NORMAL)
