"""
Pure, Deterministic Thermodynamic Physics Equations for FOUL-X.
"""

import math
from typing import Tuple, Optional


def calculate_heat_duty_tube(m_tube: float, cp_tube: float, t_tube_in: float, t_tube_out: float) -> Optional[float]:
    """
    Computes heat absorbed by cold fluid in tube side (Watts).
    Sign convention: Q_tube >= 0 when T_tube_out >= T_tube_in.
    """
    if not (math.isfinite(m_tube) and math.isfinite(cp_tube) and math.isfinite(t_tube_in) and math.isfinite(t_tube_out)):
        return None
    if m_tube < 0 or cp_tube <= 0:
        return None
    return m_tube * cp_tube * (t_tube_out - t_tube_in)


def calculate_heat_duty_shell(m_shell: float, cp_shell: float, t_shell_in: float, t_shell_out: float) -> Optional[float]:
    """
    Computes heat released by hot fluid in shell side (Watts).
    Sign convention: Q_shell >= 0 when T_shell_in >= T_shell_out.
    """
    if not (math.isfinite(m_shell) and math.isfinite(cp_shell) and math.isfinite(t_shell_in) and math.isfinite(t_shell_out)):
        return None
    if m_shell < 0 or cp_shell <= 0:
        return None
    return m_shell * cp_shell * (t_shell_in - t_shell_out)


def calculate_thermal_discrepancy(q_tube: Optional[float], q_shell: Optional[float]) -> Optional[float]:
    """
    Calculates relative thermal balance error between tube and shell duties.
    Formula: |Q_tube - Q_shell| / max(Q_tube, Q_shell)
    Both Q_tube and Q_shell are expected to be positive (non-negative) values.
    """
    if q_tube is None or q_shell is None:
        return None
    if not (math.isfinite(q_tube) and math.isfinite(q_shell)):
        return None
    max_q = max(abs(q_tube), abs(q_shell))
    if max_q == 0:
        return 0.0
    return abs(q_tube - q_shell) / max_q


def calculate_lmtd(t_shell_in: float, t_shell_out: float, t_tube_in: float, t_tube_out: float) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Computes Logarithmic Mean Temperature Difference (LMTD) assuming counter-current flow arrangement.
    
    Definitions:
    delta_t_1 = T_shell_in - T_tube_out
    delta_t_2 = T_shell_out - T_tube_in
    
    Returns:
    (delta_t_1, delta_t_2, lmtd)
    If delta_t_1 <= 0 or delta_t_2 <= 0, lmtd is invalid and returns (delta_t_1, delta_t_2, None).
    """
    if not (math.isfinite(t_shell_in) and math.isfinite(t_shell_out) and math.isfinite(t_tube_in) and math.isfinite(t_tube_out)):
        return None, None, None

    dt1 = t_shell_in - t_tube_out
    dt2 = t_shell_out - t_tube_in

    if dt1 <= 0 or dt2 <= 0:
        return dt1, dt2, None

    if abs(dt1 - dt2) < 1e-6:
        return dt1, dt2, dt1

    try:
        lmtd = (dt1 - dt2) / math.log(dt1 / dt2)
        if math.isfinite(lmtd) and lmtd > 0:
            return dt1, dt2, lmtd
        return dt1, dt2, None
    except Exception:
        return dt1, dt2, None


def calculate_ua(q_tube: Optional[float], lmtd: Optional[float]) -> Optional[float]:
    """
    Computes overall thermal conductance UA = Q_tube / LMTD (W/K).
    """
    if q_tube is None or lmtd is None:
        return None
    if not (math.isfinite(q_tube) and math.isfinite(lmtd)):
        return None
    if lmtd <= 0 or q_tube <= 0:
        return None
    return q_tube / lmtd


def calculate_rf_derived(ua: Optional[float], ua_clean_ref: Optional[float]) -> Tuple[Optional[float], Optional[float]]:
    """
    Computes derived fouling-resistance proxy R_f_derived and relative UA ratio.
    
    R_f_derived = (1 / UA) - (1 / UA_clean_ref)
    rf_relative = UA / UA_clean_ref
    """
    if ua is None or ua_clean_ref is None:
        return None, None
    if not (math.isfinite(ua) and math.isfinite(ua_clean_ref)):
        return None, None
    if ua <= 0 or ua_clean_ref <= 0:
        return None, None

    rf_derived = (1.0 / ua) - (1.0 / ua_clean_ref)
    rf_relative = ua / ua_clean_ref
    return rf_derived, rf_relative
