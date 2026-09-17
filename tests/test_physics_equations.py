"""
Unit Tests for Pure Thermodynamic Physics Equations in FOUL-X.
"""

import math
import pytest
from src.physics.equations import (
    calculate_heat_duty_tube,
    calculate_heat_duty_shell,
    calculate_thermal_discrepancy,
    calculate_lmtd,
    calculate_ua,
    calculate_rf_derived,
)


def test_heat_duty_tube_and_shell_sign_conventions():
    # Tube side: cold fluid heated from 150C to 170C
    q_tube = calculate_heat_duty_tube(m_tube=100.0, cp_tube=2000.0, t_tube_in=150.0, t_tube_out=170.0)
    assert q_tube == 4000000.0, f"Expected Q_tube=4.0MW, got {q_tube}"
    assert q_tube > 0

    # Shell side: hot fluid cooled from 250C to 200C
    q_shell = calculate_heat_duty_shell(m_shell=50.0, cp_shell=4000.0, t_shell_in=250.0, t_shell_out=200.0)
    assert q_shell == 10000000.0, f"Expected Q_shell=10.0MW, got {q_shell}"
    assert q_shell > 0


def test_thermal_discrepancy_metric():
    q_t = 9.0e6
    q_s = 10.0e6
    err = calculate_thermal_discrepancy(q_t, q_s)
    expected_err = abs(9.0e6 - 10.0e6) / 10.0e6  # 0.10 (10%)
    assert err == pytest.approx(expected_err, rel=1e-5)


def test_lmtd_counter_current_calculation():
    # T_s_in=200, T_s_out=150, T_t_in=100, T_t_out=140
    # dt1 = 200 - 140 = 60
    # dt2 = 150 - 100 = 50
    dt1, dt2, lmtd = calculate_lmtd(t_shell_in=200.0, t_shell_out=150.0, t_tube_in=100.0, t_tube_out=140.0)
    assert dt1 == 60.0
    assert dt2 == 50.0
    expected_lmtd = (60.0 - 50.0) / math.log(60.0 / 50.0)
    assert lmtd == pytest.approx(expected_lmtd, rel=1e-5)


def test_lmtd_near_zero_dt_difference():
    # dt1 = 50.0, dt2 = 50.0 -> LMTD should equal 50.0
    dt1, dt2, lmtd = calculate_lmtd(t_shell_in=190.0, t_shell_out=150.0, t_tube_in=100.0, t_tube_out=140.0)
    assert dt1 == 50.0
    assert dt2 == 50.0
    assert lmtd == 50.0


def test_lmtd_invalid_domain_negative_dt():
    # Temperature crossover (invalid for counter-current heat transfer)
    dt1, dt2, lmtd = calculate_lmtd(t_shell_in=130.0, t_shell_out=150.0, t_tube_in=100.0, t_tube_out=140.0)
    assert dt1 == -10.0
    assert lmtd is None, "LMTD must be None for invalid temperature difference domain!"


def test_zero_flow_and_nonfinite_inputs():
    assert calculate_heat_duty_tube(m_tube=0.0, cp_tube=2000.0, t_tube_in=150.0, t_tube_out=170.0) == 0.0
    assert calculate_heat_duty_tube(m_tube=-10.0, cp_tube=2000.0, t_tube_in=150.0, t_tube_out=170.0) is None
    assert calculate_heat_duty_tube(m_tube=float("nan"), cp_tube=2000.0, t_tube_in=150.0, t_tube_out=170.0) is None
    assert calculate_heat_duty_tube(m_tube=100.0, cp_tube=2000.0, t_tube_in=float("inf"), t_tube_out=170.0) is None


def test_ua_and_rf_derived():
    ua = calculate_ua(q_tube=1000000.0, lmtd=50.0)
    assert ua == 20000.0

    rf_derived, rf_rel = calculate_rf_derived(ua=20000.0, ua_clean_ref=25000.0)
    expected_rf = (1.0 / 20000.0) - (1.0 / 25000.0)  # 5e-5 - 4e-5 = 1e-5
    assert rf_derived == pytest.approx(expected_rf, rel=1e-5)
    assert rf_rel == pytest.approx(0.8, rel=1e-5)
