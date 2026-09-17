import pytest
from src.foulx.replay.clock import ReplayClock

def test_replay_clock_initialization():
    clock = ReplayClock(min_timestamp=0.0, max_timestamp=63999.0, step_hours=1.0)
    assert clock.current_timestamp == 0.0
    assert clock.is_playing is False

def test_replay_clock_stepping():
    clock = ReplayClock(min_timestamp=0.0, max_timestamp=63999.0, step_hours=1.0)
    assert clock.step_forward() == 1.0
    assert clock.step_forward() == 2.0
    assert clock.step_backward() == 1.0

def test_replay_clock_seek_and_bounds():
    clock = ReplayClock(min_timestamp=0.0, max_timestamp=63999.0, step_hours=1.0)
    assert clock.seek(45000.0) == 45000.0
    assert clock.current_timestamp == 45000.0

    with pytest.raises(ValueError, match="out of valid dataset range"):
        clock.seek(70000.0)

    with pytest.raises(ValueError, match="out of valid dataset range"):
        clock.seek(-10.0)

def test_replay_clock_reset():
    clock = ReplayClock(min_timestamp=0.0, max_timestamp=63999.0, step_hours=1.0)
    clock.seek(50000.0)
    clock.start()
    assert clock.is_playing is True
    assert clock.reset() == 0.0
    assert clock.is_playing is False
