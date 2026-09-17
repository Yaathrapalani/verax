import pytest
from src.foulx.decision.thresholds import DecisionThresholdConfig, DEFAULT_DECISION_THRESHOLDS

def test_decision_threshold_config():
    cfg = DecisionThresholdConfig(rf_threshold=1.5e-7, planning_horizon_hours=24, exchanger_id="E01")
    assert cfg.rf_threshold == 1.5e-7
    assert cfg.planning_horizon_hours == 24
    assert cfg.exchanger_id == "E01"

def test_default_thresholds_exist():
    for tag in ["E01", "E02", "E03", "E04", "E05"]:
        assert tag in DEFAULT_DECISION_THRESHOLDS
        assert DEFAULT_DECISION_THRESHOLDS[tag].rf_threshold > 0.0
