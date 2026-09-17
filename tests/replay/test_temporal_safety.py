import pytest
from src.foulx.replay.schemas import ReplayMode
from src.foulx.replay.service import ReplayService

def test_temporal_safety_invariants():
    """
    Verifies temporal safety invariants:
    At timestamp t:
    1. Raw state reference contains ONLY data from t <= timestamp.
    2. No future observations are exposed as current state.
    3. Future ground truth Rf is not present in live/replay measurement structures.
    """
    service = ReplayService()
    test_timestamps = [44799.0, 44800.0, 45000.0, 54399.0, 54400.0]

    for t in test_timestamps:
        snap = service.get_snapshot(t, "E01", ReplayMode.NORMAL)

        # 1. Check raw state reference timestamp
        assert snap.raw_state_reference["Time_hr"] == t

        # 2. Check physics state timestamp
        assert snap.physics_state.timestamp == t

        # 3. Check forecast reference timestamp
        for f in snap.forecast_state:
            assert f.timestamp == t
            assert f.input_window_end == t

        # 4. Check reliability & decision timestamps
        assert snap.reliability_state.timestamp == t
        assert snap.decision_state.timestamp == t

        # 5. Check no future ground truth is exposed as current measurement
        assert "actual_future_rf" not in snap.raw_state_reference
        assert "actual_future_rf" not in snap.physics_state.model_dump()
