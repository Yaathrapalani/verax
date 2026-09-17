"""
Physics State Estimator Engine for FOUL-X.
Supports single-record real-time execution and historical batch dataset processing.
"""

from typing import Dict, Any, List, Optional
import pandas as pd

import numpy as np
from src.physics.schemas import (
    StateValidity,
    ThermalState,
    FoulingState,
    DataQualityState,
    AvailabilityState,
    ProvenanceState,
    CanonicalExchangerState,
)
from src.physics.equations import (
    calculate_heat_duty_tube,
    calculate_heat_duty_shell,
    calculate_thermal_discrepancy,
    calculate_lmtd,
    calculate_ua,
    calculate_rf_derived,
)
from src.physics.validators import validate_physics_inputs

EXCHANGER_MAPPING = {
    "E01": "HeavyNaphtha",
    "E02": "Kero",
    "E03": "LightDiesel",
    "E04": "LVGO",
    "E05": "HeavyDiesel",
}


class PhysicsStateEstimator:
    """
    Deterministic Physics State Estimator Engine.
    """

    def __init__(self, ua_clean_references: Optional[Dict[str, float]] = None):
        """
        Initialize estimator with optional exchanger-specific UA_clean reference dict.
        Example: {'E01': 207061.2, 'E02': 213435.9, ...}
        """
        self.ua_clean_references: Dict[str, float] = ua_clean_references or {}

    def fit_baseline_from_dataframe(self, df: pd.DataFrame, clean_window_hours: float = 100.0) -> Dict[str, float]:
        """
        Calibrates exchanger-specific UA_clean_reference baselines strictly using initial
        training timesteps (Time_hr <= clean_window_hours).
        """
        clean_df = df[df["Time_hr"] <= clean_window_hours]
        references = {}

        for tag, shell_name in EXCHANGER_MAPPING.items():
            m_t = clean_df[f"{tag}_Crude_Tube_m_kg_s"]
            cp_t = clean_df[f"{tag}_Crude_Tube_Cp_J_kgK"]
            t_t_in = clean_df[f"{tag}_Crude_Tube_T_In_degC"]
            t_t_out = clean_df[f"{tag}_Crude_Tube_T_Out_degC"]

            m_s = clean_df[f"{tag}_{shell_name}_Shell_m_kg_s"]
            cp_s = clean_df[f"{tag}_{shell_name}_Shell_Cp_J_kgK"]
            t_s_in = clean_df[f"{tag}_{shell_name}_Shell_T_In_degC"]
            t_s_out = clean_df[f"{tag}_{shell_name}_Shell_T_Out_degC"]

            Q_t = m_t * cp_t * (t_t_out - t_t_in)
            dt1 = t_s_in - t_t_out
            dt2 = t_s_out - t_t_in
            lmtd = (dt1 - dt2) / (pd.Series(dt1 / dt2).apply(lambda x: np.log(x) if x > 0 else np.nan))
            UA = Q_t / lmtd

            ua_clean_ref = float(UA.mean())
            references[tag] = ua_clean_ref

        self.ua_clean_references = references
        return references

    def process_record(self, record: Dict[str, Any], exchanger_id: str) -> CanonicalExchangerState:
        """
        Processes a single historian record for one exchanger (Real-time capability).
        """
        if exchanger_id not in EXCHANGER_MAPPING:
            raise ValueError(f"Unknown exchanger_id {exchanger_id}. Supported: {list(EXCHANGER_MAPPING.keys())}")

        shell_name = EXCHANGER_MAPPING[exchanger_id]
        ua_clean_ref = self.ua_clean_references.get(exchanger_id)

        # Validate inputs & determine validity state
        primary_status, reasons, valid_cnt, invalid_cnt = validate_physics_inputs(
            record, exchanger_id, shell_name, ua_clean_ref
        )

        timestamp = float(record.get("Time_hr", 0.0))

        source_vars = [
            "Time_hr",
            f"{exchanger_id}_Crude_Tube_m_kg_s",
            f"{exchanger_id}_Crude_Tube_Cp_J_kgK",
            f"{exchanger_id}_Crude_Tube_T_In_degC",
            f"{exchanger_id}_Crude_Tube_T_Out_degC",
            f"{exchanger_id}_{shell_name}_Shell_m_kg_s",
            f"{exchanger_id}_{shell_name}_Shell_Cp_J_kgK",
            f"{exchanger_id}_{shell_name}_Shell_T_In_degC",
            f"{exchanger_id}_{shell_name}_Shell_T_Out_degC",
        ]

        if primary_status != StateValidity.VALID:
            return CanonicalExchangerState(
                timestamp=timestamp,
                exchanger_id=exchanger_id,
                thermal=ThermalState(ua_clean_reference=ua_clean_ref),
                fouling=FoulingState(),
                data_quality=DataQualityState(
                    valid_input_count=valid_cnt,
                    invalid_input_count=invalid_cnt,
                    primary_status=primary_status,
                    reasons=reasons,
                ),
                availability=AvailabilityState(),
                provenance=ProvenanceState(source_variables=source_vars),
            )

        # Extract values
        m_t = float(record[f"{exchanger_id}_Crude_Tube_m_kg_s"])
        cp_t = float(record[f"{exchanger_id}_Crude_Tube_Cp_J_kgK"])
        t_t_in = float(record[f"{exchanger_id}_Crude_Tube_T_In_degC"])
        t_t_out = float(record[f"{exchanger_id}_Crude_Tube_T_Out_degC"])

        m_s = float(record[f"{exchanger_id}_{shell_name}_Shell_m_kg_s"])
        cp_s = float(record[f"{exchanger_id}_{shell_name}_Shell_Cp_J_kgK"])
        t_s_in = float(record[f"{exchanger_id}_{shell_name}_Shell_T_In_degC"])
        t_s_out = float(record[f"{exchanger_id}_{shell_name}_Shell_T_Out_degC"])

        # Execute equations
        q_tube = calculate_heat_duty_tube(m_t, cp_t, t_t_in, t_t_out)
        q_shell = calculate_heat_duty_shell(m_s, cp_s, t_s_in, t_s_out)
        thermal_err = calculate_thermal_discrepancy(q_tube, q_shell)
        dt1, dt2, lmtd = calculate_lmtd(t_s_in, t_s_out, t_t_in, t_t_out)
        ua = calculate_ua(q_tube, lmtd)
        rf_derived, rf_relative = calculate_rf_derived(ua, ua_clean_ref)

        thermal_state = ThermalState(
            q_tube=q_tube,
            q_shell=q_shell,
            thermal_balance_error=thermal_err,
            delta_t_1=dt1,
            delta_t_2=dt2,
            lmtd=lmtd,
            ua=ua,
            ua_clean_reference=ua_clean_ref,
        )

        fouling_state = FoulingState(
            rf_derived=rf_derived,
            rf_relative_to_reference=rf_relative,
        )

        data_quality_state = DataQualityState(
            valid_input_count=valid_cnt,
            invalid_input_count=invalid_cnt,
            primary_status=primary_status,
            reasons=reasons,
        )

        return CanonicalExchangerState(
            timestamp=timestamp,
            exchanger_id=exchanger_id,
            thermal=thermal_state,
            fouling=fouling_state,
            data_quality=data_quality_state,
            availability=AvailabilityState(),
            provenance=ProvenanceState(source_variables=source_vars),
        )

    def process_dataframe(self, df: pd.DataFrame) -> List[CanonicalExchangerState]:
        """
        Processes a full historical DataFrame (Batch dataset processing).
        """
        if not self.ua_clean_references:
            self.fit_baseline_from_dataframe(df)

        states: List[CanonicalExchangerState] = []
        for _, row in df.iterrows():
            record = row.to_dict()
            for tag in EXCHANGER_MAPPING.keys():
                state = self.process_record(record, tag)
                states.append(state)

        return states
