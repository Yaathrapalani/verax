"""
Maintenance Policies Implementation for FOUL-X M7.0 Evaluation Experiment.

Implements three explicit maintenance policies:
1. FIXED — Configured fixed-policy baseline (reference)
2. UNGATED — M4 Forecast -> M6 Decision (bypassing M5 Reliability Gate)
3. GATED — M4 Forecast -> M5 Reliability Gate -> M6 Decision (or FIXED fallback on ABSTAIN)
"""

from typing import Dict, Any, List, Optional
import pandas as pd

from src.physics.schemas import CanonicalExchangerState
from src.forecast.schemas import ForecastResult, ForecastStatus
from src.foulx.gate.schemas import ReliabilityResult, GateStatus, ForecastReference, GateProvenance
from src.foulx.gate.evaluator import ReliabilityGateEvaluator
from src.foulx.decision.schemas import DecisionResult, DecisionState, DecisionProvenance
from src.foulx.decision.evaluator import DecisionEngineEvaluator
from src.foulx.decision.thresholds import DecisionThresholdConfig
from src.foulx.evaluation.schemas import PolicyType


class FixedPolicy:
    """
    POLICY 1 — FIXED (Configured fixed-policy baseline)

    Represent the existing baseline/fallback policy.
    Reference policy: Recommend cleaning review if current Rf_derived >= threshold,
    or at fixed interval ticks (e.g. periodic fixed maintenance rule).
    """

    def __init__(self, threshold_config: DecisionThresholdConfig):
        self.threshold_config = threshold_config

    def evaluate(self, current_rf: Optional[float], timestamp: float) -> DecisionState:
        """
        Determines action based strictly on current state and configured fixed rule.
        Does NOT use M4 forecast or M5 gate.
        """
        if current_rf is not None and current_rf >= self.threshold_config.rf_threshold:
            return DecisionState.CLEANING_REVIEW
        return DecisionState.OPERATE


class UngatedPolicy:
    """
    POLICY 2 — UNGATED (AI Forecast -> M6 Decision without M5 Gate)

    The forecast is allowed to influence the decision without M5 reliability gating.
    Uses existing M4 forecast and M6 decision semantics with a dummy PASS gate.
    """

    def __init__(self, decision_evaluator: DecisionEngineEvaluator):
        self.decision_evaluator = decision_evaluator

    def evaluate(
        self,
        canonical_state: CanonicalExchangerState,
        forecast_results: List[ForecastResult],
        threshold_config: DecisionThresholdConfig,
    ) -> DecisionResult:
        """
        Evaluates decision bypassing M5 Reliability Gate checks.
        Creates a synthetic PASS gate result to allow M6 evaluation.
        """
        exchanger_id = threshold_config.exchanger_id
        timestamp = canonical_state.timestamp

        # Create synthetic PASS gate result to bypass gate
        synthetic_pass_gate = ReliabilityResult(
            timestamp=timestamp,
            exchanger_id=exchanger_id,
            status=GateStatus.PASS,
            checks=[],
            reason_codes=[],
            evidence={"ungated_bypass": True},
            forecast_reference=ForecastReference(
                exchanger_id=exchanger_id,
                timestamp=timestamp,
                horizon_hours=threshold_config.planning_horizon_hours,
                prediction=forecast_results[0].prediction if forecast_results else None,
            ),
            provenance=GateProvenance(),
        )

        return self.decision_evaluator.evaluate_decision(
            reliability_result=synthetic_pass_gate,
            canonical_state=canonical_state,
            forecast_results=forecast_results,
            threshold_config=threshold_config,
        )


class GatedPolicy:
    """
    POLICY 3 — GATED (M4 Forecast -> M5 Gate -> M6 Decision, fallback to FIXED on ABSTAIN)

    If M5 = PASS: allow M6 decision.
    If M5 = ABSTAIN: fall back to the configured fixed policy.
    This fallback behavior is the core experimental treatment.
    """

    def __init__(
        self,
        gate_evaluator: ReliabilityGateEvaluator,
        decision_evaluator: DecisionEngineEvaluator,
        fixed_policy: FixedPolicy,
    ):
        self.gate_evaluator = gate_evaluator
        self.decision_evaluator = decision_evaluator
        self.fixed_policy = fixed_policy

    def evaluate(
        self,
        raw_record: Dict[str, Any],
        required_fields: List[str],
        tag: str,
        shell_name: str,
        canonical_state: CanonicalExchangerState,
        forecast_results: List[ForecastResult],
        feature_vector: Optional[pd.Series],
        threshold_config: DecisionThresholdConfig,
    ) -> Dict[str, Any]:
        """
        Evaluates GATED policy with explicit fallback to FIXED baseline on ABSTAIN.
        Returns dictionary containing:
        - decision_result: DecisionResult
        - reliability_result: ReliabilityResult
        - fallback_used: bool
        - action: DecisionState
        """
        # 1. Run authoritative M5 Reliability Gate
        forecast_ref_obj = forecast_results[0] if forecast_results else ForecastResult(
            exchanger_id=threshold_config.exchanger_id,
            timestamp=canonical_state.timestamp,
            horizon_hours=threshold_config.planning_horizon_hours,
            prediction=None,
            input_window_start=canonical_state.timestamp,
            input_window_end=canonical_state.timestamp,
            status=ForecastStatus.UNAVAILABLE,
            method="RidgeRegression",
        )

        reliability_res = self.gate_evaluator.evaluate_reliability(
            raw_record=raw_record,
            required_fields=required_fields,
            tag=tag,
            shell_name=shell_name,
            canonical_state=canonical_state,
            forecast_result=forecast_ref_obj,
            feature_vector=feature_vector,
        )

        current_rf = canonical_state.fouling.rf_derived if (canonical_state and canonical_state.fouling) else None

        if reliability_res.status == GateStatus.PASS:
            # Pass -> allow M6 decision
            decision_res = self.decision_evaluator.evaluate_decision(
                reliability_result=reliability_res,
                canonical_state=canonical_state,
                forecast_results=forecast_results,
                threshold_config=threshold_config,
            )
            return {
                "decision_result": decision_res,
                "reliability_result": reliability_res,
                "fallback_used": False,
                "action": decision_res.decision,
            }
        else:
            # Abstain -> Fall back to FIXED policy
            fallback_action = self.fixed_policy.evaluate(current_rf, canonical_state.timestamp)
            
            # Construct ABSTAIN decision result reflecting fallback
            decision_res = DecisionResult(
                timestamp=canonical_state.timestamp,
                exchanger_id=threshold_config.exchanger_id,
                decision=DecisionState.ABSTAIN, # Internal decision state is ABSTAIN
                reliability_status=GateStatus.ABSTAIN,
                current_rf_derived=current_rf,
                forecast_horizon_hours=threshold_config.planning_horizon_hours,
                threshold_rf=threshold_config.rf_threshold,
                threshold_crossing=False,
                estimated_crossing_horizon_hours=None,
                reason_codes=[],
                evidence={"fallback_policy": "FIXED", "fallback_action": fallback_action.value},
                provenance=DecisionProvenance(),
            )
            return {
                "decision_result": decision_res,
                "reliability_result": reliability_res,
                "fallback_used": True,
                "action": fallback_action, # Executed action is fallback action
            }
