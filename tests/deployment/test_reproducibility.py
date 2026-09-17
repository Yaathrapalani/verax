import pytest
from src.foulx.replay.schemas import ReplayMode
from src.foulx.replay.service import ReplayService
from src.foulx.api.app import get_replay_service, health_check, get_replay_snapshot


def test_native_vs_api_reproducibility():
    """
    Verifies that calling ReplayService natively vs invoking API handlers returns
    100% identical canonical engineering state for E02 / t=45000 / NORMAL and SHIFTED.
    """
    service = get_replay_service()

    # 1. NORMAL mode comparison
    native_normal = service.get_snapshot(45000.0, "E02", ReplayMode.NORMAL).to_dict()
    api_normal = get_replay_snapshot(time_hr=45000.0, exchanger_id="E02", scenario="NORMAL")

    assert native_normal["timestamp"] == api_normal["timestamp"]
    assert native_normal["exchanger_id"] == api_normal["exchanger_id"]
    assert native_normal["physics_state"] == api_normal["physics_state"]
    assert native_normal["reliability_state"] == api_normal["reliability_state"]
    assert native_normal["decision_state"] == api_normal["decision_state"]

    # 2. SHIFTED mode comparison
    native_shifted = service.get_snapshot(45000.0, "E02", ReplayMode.SHIFTED).to_dict()
    api_shifted = get_replay_snapshot(time_hr=45000.0, exchanger_id="E02", scenario="SHIFTED")

    assert native_shifted["reliability_state"]["status"] == "ABSTAIN"
    assert api_shifted["reliability_state"]["status"] == "ABSTAIN"
    assert native_shifted["decision_state"]["decision"] == "ABSTAIN"
    assert api_shifted["decision_state"]["decision"] == "ABSTAIN"
    assert native_shifted == api_shifted


def test_api_health_check_endpoint():
    health = health_check()
    assert health["status"] == "healthy"
    assert health["artifacts_loaded"] is True
    assert health["plant_connectivity"] == "DISCONNECTED_PROTOTYPE_MODE"
    assert health["dataset_checksum"] == "c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9"
