"""
Unit tests for FOUL-X M11.0 Red-Team Failure Injector.
"""

import pytest
import pandas as pd
import numpy as np

from src.foulx.redteam.failure_injector import RedTeamFailureInjector
from src.foulx.redteam.reason_codes import RedTeamScenarioCode
from src.foulx.gate.schemas import GateStatus
from src.foulx.decision.schemas import DecisionState


def test_failure_injector_missing_critical_measurement():
    injector = RedTeamFailureInjector()
    record = {"E01_Crude_Tube_T_In_degC": 150.0, "E01_Crude_Tube_T_Out_degC": 120.0}
    corrupted = injector.inject_missing_critical_measurement(record, tag="E01")
    assert "E01_Crude_Tube_T_In_degC" not in corrupted


def test_failure_injector_invalid_sensor_value():
    injector = RedTeamFailureInjector()
    record = {"E01_Crude_Tube_T_In_degC": 150.0}
    corrupted = injector.inject_invalid_sensor_value(record, tag="E01")
    assert corrupted["E01_Crude_Tube_T_In_degC"] == 999.0


def test_failure_injector_regime_shift():
    injector = RedTeamFailureInjector()
    record = {"E01_Crude_Tube_T_In_degC": 150.0}
    features = pd.Series({"E01_Crude_Tube_T_In_degC": 150.0})
    rec, feat = injector.inject_regime_shift_ood(record, features, tag="E01")
    assert feat["E01_Crude_Tube_T_In_degC"] > features["E01_Crude_Tube_T_In_degC"]
