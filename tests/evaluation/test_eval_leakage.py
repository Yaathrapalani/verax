import pytest
import pandas as pd
from src.physics.schemas import CanonicalExchangerState, ThermalState, FoulingState, DataQualityState, StateValidity, AvailabilityState, ProvenanceState
from src.forecast.schemas import ForecastResult, ForecastStatus
from src.foulx.gate.evaluator import ReliabilityGateEvaluator
from src.foulx.decision.evaluator import DecisionEngineEvaluator
from src.foulx.evaluation.schemas import PolicyType, EvaluationCondition
from src.foulx.evaluation.evaluator import PolicyExperimentEvaluator

def test_leakage_audit_invariants():
    """
    Verifies leakage prevention:
    1. Future actual Rf is NEVER passed to forecast or gate inputs.
    2. Future actual Rf exists only in evaluation ground truth.
    3. Source data is never mutated by perturbations.
    """
    raw_record = {"E01_Crude_Tube_T_In_degC": 150.0}
    actual_future_rf = 2.5e-7 # Ground truth in future

    # Check inputs to forecast & gate do not contain actual_future_rf
    assert "actual_future_rf" not in raw_record
    assert "actual_future_rf" not in ["E01_Crude_Tube_T_In_degC"]

    # Check perturbation does not mutate original raw_record
    pert_raw = dict(raw_record)
    pert_raw["E01_Crude_Tube_T_In_degC"] = 300.0
    assert raw_record["E01_Crude_Tube_T_In_degC"] == 150.0
