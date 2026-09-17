import pytest
from src.foulx.replay.schemas import ReplaySnapshot, ReplayMode, ReplayManifest, ReplayProvenance
from src.foulx.replay.service import ReplayService

def test_replay_snapshot_schema_instantiation():
    service = ReplayService()
    snap = service.get_snapshot(45000.0, exchanger_id="E01", scenario_mode=ReplayMode.NORMAL)
    assert snap.timestamp == 45000.0
    assert snap.exchanger_id == "E01"
    assert snap.scenario_mode == ReplayMode.NORMAL
    assert snap.physics_state.timestamp == 45000.0
    assert snap.reliability_state.timestamp == 45000.0
    assert snap.decision_state.timestamp == 45000.0
    assert snap.provenance.no_future_leakage is True

def test_replay_manifest_generation():
    service = ReplayService()
    manifest = service.get_manifest()
    assert manifest.min_timestamp == 0.0
    assert manifest.max_timestamp == 63999.0
    assert manifest.train_boundary == {"start": 0.0, "end": 44799.0}
    assert manifest.test_boundary == {"start": 54400.0, "end": 63999.0}
