"""
Failure Injector for FOUL-X M11.0 Red-Team Harness.

Applies controlled in-memory perturbations and corruptions to copied records & feature vectors
without mutating canonical dataset files or baseline model parameters.
"""

import math
from typing import Dict, Any, List, Tuple
import pandas as pd

from src.foulx.evaluation.perturbations import SyntheticRegimeShiftPerturber


class RedTeamFailureInjector:
    """
    In-memory failure injector for Red-Team validation.
    All operations return NEW copied dictionaries/Series.
    """

    def __init__(self):
        self.perturber = SyntheticRegimeShiftPerturber(shift_factor=6.0)

    def inject_missing_critical_measurement(
        self, raw_record: Dict[str, Any], tag: str = "E01"
    ) -> Dict[str, Any]:
        """Corrupts record by removing a critical required input field (e.g. Tube_T_In)."""
        corrupted = dict(raw_record)
        key_to_remove = f"{tag}_Crude_Tube_T_In_degC"
        if key_to_remove in corrupted:
            del corrupted[key_to_remove]
        return corrupted

    def inject_invalid_sensor_value(
        self, raw_record: Dict[str, Any], tag: str = "E01"
    ) -> Dict[str, Any]:
        """Corrupts record by setting a sensor value out of physical bounds or non-finite (e.g. T_In = 999.0 degC)."""
        corrupted = dict(raw_record)
        corrupted[f"{tag}_Crude_Tube_T_In_degC"] = 999.0 # Bounds [0, 450]
        return corrupted

    def inject_thermal_physics_inconsistency(
        self, raw_record: Dict[str, Any], tag: str = "E01", shell_name: str = "Shell"
    ) -> Dict[str, Any]:
        """
        Corrupts record to violate thermodynamic heat balance |Q_t - Q_s|/max(Q) > 0.05
        or temperature cross (e.g. Shell T_Out < Tube T_In).
        """
        corrupted = dict(raw_record)
        # Force huge temperature inversion on shell side
        corrupted[f"{tag}_{shell_name}_Shell_T_In_degC"] = 100.0
        corrupted[f"{tag}_{shell_name}_Shell_T_Out_degC"] = 350.0
        corrupted[f"{tag}_Crude_Tube_T_In_degC"] = 300.0
        corrupted[f"{tag}_Crude_Tube_T_Out_degC"] = 120.0
        return corrupted

    def inject_regime_shift_ood(
        self, raw_record: Dict[str, Any], feature_vector: pd.Series, tag: str = "E01"
    ) -> Tuple[Dict[str, Any], pd.Series]:
        """Applies established +6.0 std regime shift using existing M7 perturber."""
        perturbed_rec = self.perturber.perturb_raw_record(raw_record, tag=tag)
        perturbed_feat = self.perturber.perturb_feature_vector(feature_vector)
        return perturbed_rec, perturbed_feat

    def inject_multiple_failures(
        self, raw_record: Dict[str, Any], feature_vector: pd.Series, tag: str = "E01"
    ) -> Tuple[Dict[str, Any], pd.Series]:
        """
        Injects multiple simultaneous failures: missing field + out-of-bounds sensor + regime shift.
        Useful to verify M5 reason code ordering precedence.
        """
        rec = dict(raw_record)
        # 1. Missing field
        del rec[f"{tag}_Crude_Tube_m_kg_s"]
        # 2. Invalid sensor
        rec[f"{tag}_Crude_Tube_T_In_degC"] = 999.0
        # 3. Regime shift feature vector
        _, feat = self.inject_regime_shift_ood(raw_record, feature_vector, tag=tag)
        return rec, feat
