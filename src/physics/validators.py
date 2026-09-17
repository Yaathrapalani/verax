"""
Physics Input and Numerical Domain Validation Functions.
"""

import math
from typing import Dict, Any, List, Tuple
from src.physics.schemas import StateValidity


def validate_physics_inputs(
    record: Dict[str, Any],
    tag: str,
    shell_name: str,
    ua_clean_ref: float = None
) -> Tuple[StateValidity, List[str], int, int]:
    """
    Validates physical inputs for a heat exchanger calculation.
    Collects all numerical and physical domain failure reasons.
    
    Returns:
        (primary_status, reasons_list, valid_count, invalid_count)
    """
    reasons: List[str] = []
    
    req_keys = [
        f"{tag}_Crude_Tube_m_kg_s",
        f"{tag}_Crude_Tube_Cp_J_kgK",
        f"{tag}_Crude_Tube_T_In_degC",
        f"{tag}_Crude_Tube_T_Out_degC",
        f"{tag}_{shell_name}_Shell_m_kg_s",
        f"{tag}_{shell_name}_Shell_Cp_J_kgK",
        f"{tag}_{shell_name}_Shell_T_In_degC",
        f"{tag}_{shell_name}_Shell_T_Out_degC",
    ]

    valid_count = 0
    invalid_count = 0

    for k in req_keys:
        if k not in record or record[k] is None:
            invalid_count += 1
            reasons.append(f"MISSING_KEY:{k}")
        elif not isinstance(record[k], (int, float)) or not math.isfinite(record[k]):
            invalid_count += 1
            reasons.append(f"NONFINITE:{k}")
        else:
            valid_count += 1

    # Mass flow validation if flow key present and finite
    m_tube_key = f"{tag}_Crude_Tube_m_kg_s"
    m_shell_key = f"{tag}_{shell_name}_Shell_m_kg_s"
    if m_tube_key in record and isinstance(record[m_tube_key], (int, float)) and math.isfinite(record[m_tube_key]):
        if record[m_tube_key] <= 0:
            reasons.append("ZERO_OR_NEGATIVE_FLOW:TUBE")
    if m_shell_key in record and isinstance(record[m_shell_key], (int, float)) and math.isfinite(record[m_shell_key]):
        if record[m_shell_key] <= 0:
            reasons.append("ZERO_OR_NEGATIVE_FLOW:SHELL")

    # Temperature difference validation if temp keys present and finite
    t_t_in_key = f"{tag}_Crude_Tube_T_In_degC"
    t_t_out_key = f"{tag}_Crude_Tube_T_Out_degC"
    t_s_in_key = f"{tag}_{shell_name}_Shell_T_In_degC"
    t_s_out_key = f"{tag}_{shell_name}_Shell_T_Out_degC"

    temp_keys = [t_t_in_key, t_t_out_key, t_s_in_key, t_s_out_key]
    if all(k in record and isinstance(record[k], (int, float)) and math.isfinite(record[k]) for k in temp_keys):
        t_t_in = record[t_t_in_key]
        t_t_out = record[t_t_out_key]
        t_s_in = record[t_s_in_key]
        t_s_out = record[t_s_out_key]

        dt_tube = t_t_out - t_t_in
        dt_shell = t_s_in - t_s_out

        if dt_tube <= 0 or dt_shell <= 0:
            reasons.append("NEAR_ZERO_OR_NEGATIVE_DT")

        dt1 = t_s_in - t_t_out
        dt2 = t_s_out - t_t_in
        if dt1 <= 0 or dt2 <= 0:
            reasons.append("INVALID_LMTD_DOMAIN")

    # UA_clean reference validation
    if ua_clean_ref is None or not math.isfinite(ua_clean_ref) or ua_clean_ref <= 0:
        reasons.append("INSUFFICIENT_BASELINE")

    # Primary status determination based on priority of failure reasons
    if any(r.startswith("NONFINITE") or r.startswith("MISSING_KEY") for r in reasons):
        primary_status = StateValidity.INVALID_INPUT
    elif any(r.startswith("ZERO_OR_NEGATIVE_FLOW") for r in reasons):
        primary_status = StateValidity.ZERO_FLOW
    elif "NEAR_ZERO_OR_NEGATIVE_DT" in reasons:
        primary_status = StateValidity.NEAR_ZERO_DT
    elif "INVALID_LMTD_DOMAIN" in reasons:
        primary_status = StateValidity.INVALID_LMTD
    elif "INSUFFICIENT_BASELINE" in reasons:
        primary_status = StateValidity.INSUFFICIENT_BASELINE
    else:
        primary_status = StateValidity.VALID

    return primary_status, reasons, valid_count, invalid_count
