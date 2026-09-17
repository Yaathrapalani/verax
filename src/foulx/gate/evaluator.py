"""
Main Reliability Gate Evaluator for FOUL-X M5.0.
Orchestrates checks, enforces safety invariants, and formats canonical ReliabilityResult.
"""

from typing import Dict, Any, List, Optional
import pandas as pd

from src.physics.schemas import CanonicalExchangerState
from src.forecast.schemas import ForecastResult
from src.foulx.gate.schemas import (
    ReliabilityResult,
    GateStatus,
    CheckStatus,
    CheckResult,
    ForecastReference,
    GateProvenance,
)
from src.foulx.gate.reason_codes import ReliabilityReasonCode, REASON_CODE_ORDER
from src.foulx.gate.checks import (
    check_data_completeness,
    check_sensor_validity,
    check_physics_consistency,
    HistoricalRegimeSupportChecker,
)


class ReliabilityGateEvaluator:
    """
    FOUL-X M5.0 Reliability Gate Evaluator Engine.

    SAFETY INVARIANTS:
    1. Returns PASS iff all mandatory checks return CheckStatus.PASS and reason_codes is empty.
    2. ABSTAIN can never silently become PASS.
    3. Never issues maintenance/cleaning commands.
    4. Deterministic: identical inputs produce identical ReliabilityResult.
    """

    def __init__(self, regime_checker: Optional[HistoricalRegimeSupportChecker] = None):
        self.regime_checker = regime_checker

    def evaluate_reliability(
        self,
        raw_record: Dict[str, Any],
        required_fields: List[str],
        tag: str,
        shell_name: str,
        canonical_state: CanonicalExchangerState,
        forecast_result: ForecastResult,
        feature_vector: Optional[pd.Series] = None,
    ) -> ReliabilityResult:
        """
        Evaluates complete Reliability Gate suite for a single forecast origin.
        Executes all checks and aggregates reason codes in deterministic order.
        """
        checks: List[CheckResult] = []

        # 1. Check Data Completeness
        chk_data = check_data_completeness(raw_record, required_fields)
        checks.append(chk_data)

        # 2. Check Sensor Validity
        chk_sensor = check_sensor_validity(raw_record, tag, shell_name)
        checks.append(chk_sensor)

        # 3. Check Physics Consistency
        chk_physics = check_physics_consistency(canonical_state)
        checks.append(chk_physics)

        # 4. Check Historical Regime Support (if feature vector and fitted checker available)
        if self.regime_checker is not None and feature_vector is not None:
            chk_regime = self.regime_checker.check_regime_support(feature_vector)
            checks.append(chk_regime)

        # Aggregate reason codes in deterministic order
        unfiltered_codes = [chk.reason_code for chk in checks if chk.reason_code is not None]
        
        # Sort reason codes according to REASON_CODE_ORDER
        ordered_reason_codes = [
            code for code in REASON_CODE_ORDER if code in unfiltered_codes
        ]

        # Determine overall Gate Decision
        all_passed = all(chk.status == CheckStatus.PASS for chk in checks)
        gate_status = GateStatus.PASS if (all_passed and len(ordered_reason_codes) == 0) else GateStatus.ABSTAIN

        # Forecast Reference
        forecast_ref = ForecastReference(
            exchanger_id=forecast_result.exchanger_id,
            timestamp=forecast_result.timestamp,
            horizon_hours=forecast_result.horizon_hours,
            prediction=forecast_result.prediction,
            model_method=forecast_result.method,
        )

        provenance = GateProvenance(
            source_variables=list(raw_record.keys()),
        )

        evidence_summary = {
            "total_checks_executed": len(checks),
            "failed_checks_count": len([chk for chk in checks if chk.status == CheckStatus.FAIL]),
            "gate_decision": gate_status.value,
        }

        return ReliabilityResult(
            timestamp=forecast_result.timestamp,
            exchanger_id=forecast_result.exchanger_id,
            status=gate_status,
            checks=checks,
            reason_codes=ordered_reason_codes,
            evidence=evidence_summary,
            forecast_reference=forecast_ref,
            provenance=provenance,
        )
