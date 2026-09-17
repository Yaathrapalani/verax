"""
Individual check implementations for FOUL-X M5.0 Reliability Gate.
Contains:
1. Data Completeness Check
2. Sensor/Input Validity Check
3. Physics Consistency Check
4. Historical Regime Support Check (Train-only normalized feature space support)
"""

import math
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

from src.physics.schemas import CanonicalExchangerState, StateValidity
from src.foulx.gate.schemas import CheckResult, CheckStatus
from src.foulx.gate.reason_codes import ReliabilityReasonCode


# Documented physical ranges based on M1-B Data Contract & M2 Physics Spec
CONFIGURED_SENSOR_BOUNDS: Dict[str, Dict[str, float]] = {
  "Crude_API": {"min": 10.0, "max": 60.0},
  "Crude_Chlorides": {"min": 0.0, "max": 100.0},
  "Crude_TAN": {"min": 0.0, "max": 10.0},
  "Tube_m_kg_s": {"min": 0.1, "max": 500.0},
  "Shell_m_kg_s": {"min": 0.1, "max": 500.0},
  "Tube_T_In_degC": {"min": 0.0, "max": 450.0},
  "Tube_T_Out_degC": {"min": 0.0, "max": 450.0},
  "Shell_T_In_degC": {"min": 0.0, "max": 500.0},
  "Shell_T_Out_degC": {"min": 0.0, "max": 500.0},
}


def check_data_completeness(
    raw_record: Dict[str, Any],
    required_fields: List[str]
) -> CheckResult:
    """
    CHECK 1 — DATA COMPLETENESS
    Validates presence of all required input fields for the forecast.
    Does NOT silently impute missing values.
    """
    missing_fields = []
    for field in required_fields:
        if field not in raw_record or raw_record[field] is None:
            missing_fields.append(field)

    if missing_fields:
        return CheckResult(
            check_name="DATA_COMPLETENESS",
            status=CheckStatus.FAIL,
            reason_code=ReliabilityReasonCode.DATA_INCOMPLETE,
            evidence={
                "missing_fields": missing_fields,
                "required_count": len(required_fields),
                "missing_count": len(missing_fields),
            },
        )

    return CheckResult(
        check_name="DATA_COMPLETENESS",
        status=CheckStatus.PASS,
        reason_code=None,
        evidence={"required_fields_present": len(required_fields)},
    )


def check_sensor_validity(
    raw_record: Dict[str, Any],
    tag: str,
    shell_name: str
) -> CheckResult:
    """
    CHECK 2 — SENSOR / INPUT VALIDITY
    Checks for NaN, Infinite values, and configured physical domain violations.
    """
    violations = []
    nonfinite_fields = []

    # Check numerical finiteness and bounds on provided fields
    for k, v in raw_record.items():
        if isinstance(v, (int, float)):
            if not math.isfinite(v):
                nonfinite_fields.append(k)
                violations.append(f"Non-finite value in {k}: {v}")

    # Specific bounds check on key process variables
    tube_in = raw_record.get(f"{tag}_Crude_Tube_T_In_degC")
    tube_out = raw_record.get(f"{tag}_Crude_Tube_T_Out_degC")
    shell_in = raw_record.get(f"{tag}_{shell_name}_Shell_T_In_degC")
    shell_out = raw_record.get(f"{tag}_{shell_name}_Shell_T_Out_degC")

    tube_m = raw_record.get(f"{tag}_Crude_Tube_m_kg_s")
    shell_m = raw_record.get(f"{tag}_{shell_name}_Shell_m_kg_s")

    for val, name, bound_key in [
        (tube_in, "Tube_T_In", "Tube_T_In_degC"),
        (tube_out, "Tube_T_Out", "Tube_T_Out_degC"),
        (shell_in, "Shell_T_In", "Shell_T_In_degC"),
        (shell_out, "Shell_T_Out", "Shell_T_Out_degC"),
        (tube_m, "Tube_m", "Tube_m_kg_s"),
        (shell_m, "Shell_m", "Shell_m_kg_s"),
    ]:
        if val is not None and isinstance(val, (int, float)) and math.isfinite(val):
            bounds = CONFIGURED_SENSOR_BOUNDS[bound_key]
            if val < bounds["min"] or val > bounds["max"]:
                violations.append(f"Value {val} for {name} out of configured bounds [{bounds['min']}, {bounds['max']}]")

    if violations:
        return CheckResult(
            check_name="SENSOR_VALIDITY",
            status=CheckStatus.FAIL,
            reason_code=ReliabilityReasonCode.SENSOR_INVALID,
            evidence={
                "violations": violations,
                "nonfinite_fields": nonfinite_fields,
            },
        )

    return CheckResult(
        check_name="SENSOR_VALIDITY",
        status=CheckStatus.PASS,
        reason_code=None,
        evidence={"validated_sensor_signals": len(raw_record)},
    )


def check_physics_consistency(
    canonical_state: CanonicalExchangerState
) -> CheckResult:
    """
    CHECK 3 — PHYSICS CONSISTENCY
    Consumes existing M2 CanonicalExchangerState without duplicating equations.
    Fails if M2 primary_status is not VALID.
    """
    data_quality = canonical_state.data_quality
    primary_status = data_quality.primary_status

    if primary_status != StateValidity.VALID:
        return CheckResult(
            check_name="PHYSICS_CONSISTENCY",
            status=CheckStatus.FAIL,
            reason_code=ReliabilityReasonCode.PHYSICS_INCONSISTENT,
            evidence={
                "m2_primary_status": primary_status.value,
                "m2_reasons": data_quality.reasons,
                "thermal_balance_error": canonical_state.thermal.thermal_balance_error,
                "lmtd": canonical_state.thermal.lmtd,
                "ua": canonical_state.thermal.ua,
            },
        )

    return CheckResult(
        check_name="PHYSICS_CONSISTENCY",
        status=CheckStatus.PASS,
        reason_code=None,
        evidence={
            "m2_primary_status": primary_status.value,
            "thermal_balance_error": canonical_state.thermal.thermal_balance_error,
            "lmtd": canonical_state.thermal.lmtd,
            "ua": canonical_state.thermal.ua,
        },
    )


class HistoricalRegimeSupportChecker:
    """
    CHECK 4 — HISTORICAL REGIME SUPPORT
    Determines whether a current operating feature vector X(t) lies within the
    historical operating support of the Training set (t <= 44,799).

    METHODOLOGY (Train-Only Normalized Distance Support):
    1. Fitted ONLY on Training observations (t <= 44,799).
    2. Computes per-feature min, max, mean, std on Training set.
    3. Calculates maximum normalized deviation Z_max = max_i (|x_i - mean_i| / std_i).
    4. Compares Z_max against configured threshold (default Z_max <= 4.0 std) or range bounding.
    """

    def __init__(self, z_score_threshold: float = 4.0):
        self.z_score_threshold = z_score_threshold
        self.feature_means: Optional[pd.Series] = None
        self.feature_stds: Optional[pd.Series] = None
        self.feature_mins: Optional[pd.Series] = None
        self.feature_maxs: Optional[pd.Series] = None
        self.is_fitted: bool = False

    def fit_on_training_data(self, X_train: pd.DataFrame):
        """Fits feature statistics EXCLUSIVELY on Training split."""
        self.feature_means = X_train.mean(axis=0)
        self.feature_stds = X_train.std(axis=0).replace(0.0, 1e-6)
        self.feature_mins = X_train.min(axis=0)
        self.feature_maxs = X_train.max(axis=0)
        self.is_fitted = True

    def check_regime_support(self, x_vector: pd.Series) -> CheckResult:
        """Evaluates historical support for a single observation feature vector."""
        if not self.is_fitted:
            raise RuntimeError("HistoricalRegimeSupportChecker must be fitted on training data prior to evaluation!")

        deviations = {}
        ood_features = []

        for feat in x_vector.index:
            if feat in self.feature_means:
                val = float(x_vector[feat])
                mean = float(self.feature_means[feat])
                std = float(self.feature_stds[feat])
                z_score = abs(val - mean) / std
                deviations[feat] = z_score

                if z_score > self.z_score_threshold:
                    ood_features.append(
                        f"Feature '{feat}' value {val:.4e} has Z-score {z_score:.2f} > threshold {self.z_score_threshold}"
                    )

        if ood_features:
            return CheckResult(
                check_name="REGIME_SUPPORT",
                status=CheckStatus.FAIL,
                reason_code=ReliabilityReasonCode.REGIME_OOD,
                evidence={
                    "ood_features": ood_features,
                    "max_z_score": float(max(deviations.values())) if deviations else 0.0,
                    "z_score_threshold": self.z_score_threshold,
                },
            )

        return CheckResult(
            check_name="REGIME_SUPPORT",
            status=CheckStatus.PASS,
            reason_code=None,
            evidence={
                "max_z_score": float(max(deviations.values())) if deviations else 0.0,
                "z_score_threshold": self.z_score_threshold,
            },
        )
