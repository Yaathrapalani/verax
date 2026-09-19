"""
Unit and Determinism Tests for FOUL-X Simulation Layer.
"""

import pytest
import hashlib
from src.foulx.simulation.lifecycle import FoulingLifecycleSimulator
from src.foulx.simulation.schemas import SimulationScenarioId, SimulationEventType
from src.foulx.replay.schemas import ReplayMode
from src.foulx.gate.schemas import GateStatus
from src.foulx.decision.schemas import DecisionState


def test_simulation_determinism():
    """Verify that identical scenario inputs produce identical frame sequences."""
    sim = FoulingLifecycleSimulator()
    frames1 = sim.run_sequence(start_time_hr=63200, end_time_hr=63210, exchanger_id="E02")
    
    sim2 = FoulingLifecycleSimulator()
    frames2 = sim2.run_sequence(start_time_hr=63200, end_time_hr=63210, exchanger_id="E02")

    assert len(frames1) == len(frames2)
    for f1, f2 in zip(frames1, frames2):
        assert f1.timestamp_hr == f2.timestamp_hr
        assert f1.replay_snapshot.physics_state.fouling.rf_derived == f2.replay_snapshot.physics_state.fouling.rf_derived
        assert f1.replay_snapshot.reliability_state.status == f2.replay_snapshot.reliability_state.status
        assert f1.replay_snapshot.decision_state.decision == f2.replay_snapshot.decision_state.decision


def test_source_immutability():
    """Verify raw dataset checksum is preserved exactly."""
    data_path = "data/raw/heat_exchanger_fouling_dataset.csv"
    with open(data_path, "rb") as f:
        data_hash = hashlib.sha256(f.read()).hexdigest()
    assert data_hash == "c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9"


def test_frame_timestamp_is_real_dataset_timestamp():
    """Verify frames correspond strictly to real dataset Time_hr numbers."""
    sim = FoulingLifecycleSimulator()
    frame = sim.get_frame_at_timestamp(63241.0, "E02")
    assert frame.timestamp_hr == 63241.0
    assert frame.replay_snapshot.timestamp == 63241.0


def test_simulated_cleaning_does_not_mutate_dataset():
    """Verify demo-only reset creates simulated marker without modifying dataset."""
    sim = FoulingLifecycleSimulator()
    frame = sim.trigger_simulated_cleaning(63241.0, "E02")
    assert frame.is_simulated_cleaning_active is True
    assert frame.simulated_rf_offset == -1.0e-7
    # Re-verify file checksum
    test_source_immutability()


def test_ood_uses_existing_m7_perturbation():
    """Verify OOD mode triggers M5 REGIME_OOD -> ABSTAIN."""
    sim = FoulingLifecycleSimulator()
    frame = sim.get_frame_at_timestamp(63241.0, "E02", mode=ReplayMode.SHIFTED)
    assert frame.replay_snapshot.reliability_state.status == GateStatus.ABSTAIN
    assert frame.replay_snapshot.decision_state.decision == DecisionState.ABSTAIN
