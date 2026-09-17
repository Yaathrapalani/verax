import pytest
from src.foulx.replay.schemas import ReplayMode
from src.foulx.replay.service import ReplayService

def test_replay_service_get_and_current():
    service = ReplayService()
    snap = service.get_snapshot(45000.0, "E02", ReplayMode.NORMAL)
    assert snap.timestamp == 45000.0
    assert snap.exchanger_id == "E02"

    curr_snap = service.get_current_snapshot()
    assert curr_snap.timestamp == service.clock.current_timestamp

def test_replay_service_controls():
    service = ReplayService()
    snap1 = service.seek(100.0)
    assert snap1.timestamp == 100.0

    snap2 = service.step_forward()
    assert snap2.timestamp == 101.0

    snap3 = service.step_backward()
    assert snap3.timestamp == 100.0

    snap4 = service.reset()
    assert snap4.timestamp == 0.0
