"""
Failure-safety invariant tests for FOUL-X M11.0 Red-Team.
"""

import pytest
import hashlib
from src.foulx.redteam.harness import RedTeamHarness
from src.foulx.gate.schemas import GateStatus
from src.foulx.decision.schemas import DecisionState


def test_safety_invariant_never_recommend_cleaning_on_abstain():
    """Verify that under NO circumstances does an ABSTAIN gate result in CLEANING_REVIEW."""
    harness = RedTeamHarness()
    results, _ = harness.run_all_scenarios()
    
    for res in results:
        if res.actual_gate_status == GateStatus.ABSTAIN:
            assert res.actual_decision != DecisionState.CLEANING_REVIEW
            assert res.ai_action_withheld is True


def test_raw_dataset_hash_immutability():
    """Verify dataset SHA-256 hash matches expected value."""
    data_path = "data/raw/heat_exchanger_fouling_dataset.csv"
    with open(data_path, "rb") as f:
        data_hash = hashlib.sha256(f.read()).hexdigest()
    
    assert data_hash == "c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9"
