"""
Unit tests for FOUL-X M11.0 Red-Team Harness and 10 Failure-Safety Scenarios.
"""

import pytest
import os
from src.foulx.redteam.harness import RedTeamHarness
from src.foulx.redteam.reason_codes import RedTeamScenarioCode
from src.foulx.gate.schemas import GateStatus
from src.foulx.decision.schemas import DecisionState


def test_redteam_harness_all_10_scenarios():
    harness = RedTeamHarness()
    results, summary = harness.run_all_scenarios()
    
    assert len(results) == 10
    assert summary.total_scenarios == 10
    assert summary.passed_scenarios == 10
    assert summary.failed_scenarios == 0
    assert summary.safety_invariants_held is True
    assert summary.dataset_checksum_verified is True
    assert summary.artifact_integrity_verified is True


@pytest.mark.parametrize("scenario_idx", range(10))
def test_individual_redteam_scenario(scenario_idx):
    harness = RedTeamHarness()
    results, summary = harness.run_all_scenarios()
    res = results[scenario_idx]
    
    assert res.passed is True, f"Scenario {res.scenario_code} failed!"
    
    # Assert Safety Invariant: If Gate is ABSTAIN or Decision is ABSTAIN, AI action must be withheld
    if res.actual_gate_status == GateStatus.ABSTAIN or res.actual_decision == DecisionState.ABSTAIN:
        assert res.ai_action_withheld is True
        assert res.actual_decision in (DecisionState.ABSTAIN, DecisionState.OPERATE)
        # Ensure never CLEANING_REVIEW when ABSTAIN
        assert res.actual_decision != DecisionState.CLEANING_REVIEW
