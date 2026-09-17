import pytest
from src.foulx.replay.schemas import ReplayMode
from src.foulx.replay.service import ReplayService

def test_snapshot_determinism():
    """
    Verifies that calling get_snapshot twice on identical arguments produces 100% identical outputs.
    """
    service = ReplayService()

    for t in [44800.0, 45000.0, 54400.0]:
        for ex in ["E01", "E02", "E05"]:
            snap1 = service.get_snapshot(t, ex, ReplayMode.NORMAL)
            snap2 = service.get_snapshot(t, ex, ReplayMode.NORMAL)

            assert snap1.timestamp == snap2.timestamp
            assert snap1.exchanger_id == snap2.exchanger_id
            assert snap1.physics_state.model_dump() == snap2.physics_state.model_dump()
            assert snap1.reliability_state.model_dump() == snap2.reliability_state.model_dump()
            assert snap1.decision_state.model_dump() == snap2.decision_state.model_dump()

def test_shifted_snapshot_determinism():
    """
    Verifies that SHIFTED scenario snapshots are 100% deterministic across calls.
    """
    service = ReplayService()
    snap1 = service.get_snapshot(45000.0, "E02", ReplayMode.SHIFTED)
    snap2 = service.get_snapshot(45000.0, "E02", ReplayMode.SHIFTED)

    assert snap1.reliability_state.status == snap2.reliability_state.status
    assert snap1.decision_state.decision == snap2.decision_state.decision
    assert snap1.model_dump() == snap2.model_dump()
