"""
Main Policy Experiment Evaluator Engine for FOUL-X M7.0.

Orchestrates complete evaluation across:
- Test split (t = 54400..63999)
- 3 Policies (FIXED, UNGATED, GATED)
- 2 Conditions (SUPPORTED, SHIFTED)
"""

import uuid
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd

from src.physics.schemas import CanonicalExchangerState
from src.forecast.schemas import ForecastResult, ForecastStatus
from src.foulx.gate.schemas import GateStatus
from src.foulx.gate.evaluator import ReliabilityGateEvaluator
from src.foulx.gate.checks import HistoricalRegimeSupportChecker
from src.foulx.decision.schemas import DecisionState
from src.foulx.decision.evaluator import DecisionEngineEvaluator
from src.foulx.decision.thresholds import DecisionThresholdConfig, DEFAULT_DECISION_THRESHOLDS
from src.foulx.evaluation.schemas import (
    PolicyType,
    EvaluationCondition,
    OutcomeClass,
    PolicyEvaluationResult,
    PolicySummaryResult,
    EvaluationProvenance,
)
from src.foulx.evaluation.policies import FixedPolicy, UngatedPolicy, GatedPolicy
from src.foulx.evaluation.perturbations import SyntheticRegimeShiftPerturber
from src.foulx.evaluation.metrics import classify_outcome, compute_summary_metrics
from src.foulx.evaluation.reason_codes import EvaluationReasonCode


class PolicyExperimentEvaluator:
    """
    FOUL-X M7.0 Policy Experiment Evaluator Engine.

    SAFETY & LEAKAGE INVARIANTS:
    1. Uses test split (t in [54400, 63999]).
    2. Future actual Rf(t+h) is strictly evaluation-only ground truth.
    3. Model, gate, and decision logic remain frozen (no retraining/tuning).
    4. Deterministic execution.
    """

    def __init__(
        self,
        gate_evaluator: ReliabilityGateEvaluator,
        decision_evaluator: DecisionEngineEvaluator,
        threshold_config: Optional[DecisionThresholdConfig] = None,
        perturber: Optional[SyntheticRegimeShiftPerturber] = None,
    ):
        self.gate_evaluator = gate_evaluator
        self.decision_evaluator = decision_evaluator
        self.threshold_config = threshold_config or DEFAULT_DECISION_THRESHOLDS["E01"]
        self.perturber = perturber or SyntheticRegimeShiftPerturber()
        self.fixed_policy = FixedPolicy(self.threshold_config)
        self.ungated_policy = UngatedPolicy(self.decision_evaluator)
        self.gated_policy = GatedPolicy(
            self.gate_evaluator, self.decision_evaluator, self.fixed_policy
        )

    def evaluate_single_instance(
        self,
        raw_record: Dict[str, Any],
        required_fields: List[str],
        tag: str,
        shell_name: str,
        canonical_state: CanonicalExchangerState,
        forecast_results: List[ForecastResult],
        feature_vector: Optional[pd.Series],
        actual_future_rf: float,
        condition: EvaluationCondition,
        policy: PolicyType,
    ) -> PolicyEvaluationResult:
        """
        Evaluates a single decision timestamp t for a given policy and condition.
        """
        exchanger_id = canonical_state.exchanger_id
        timestamp = canonical_state.timestamp
        current_rf = canonical_state.fouling.rf_derived if canonical_state.fouling else 0.0
        horizon = self.threshold_config.planning_horizon_hours
        threshold = self.threshold_config.rf_threshold

        # Extract primary forecast prediction
        primary_pred = None
        for f in forecast_results:
            if f.horizon_hours == horizon:
                primary_pred = f.prediction
                break

        # Apply perturbation if SHIFTED condition
        eval_raw = raw_record
        eval_feat = feature_vector
        if condition == EvaluationCondition.SHIFTED:
            eval_raw = self.perturber.perturb_raw_record(raw_record, tag=tag)
            if feature_vector is not None:
                eval_feat = self.perturber.perturb_feature_vector(feature_vector)

        # Policy execution
        gate_status = None
        fallback_used = False
        reason_codes = [EvaluationReasonCode.TEST_SPLIT_EVALUATED]

        if condition == EvaluationCondition.SHIFTED:
            reason_codes.append(EvaluationReasonCode.SHIFTED_REGIME_OOD_TRIGGERED)

        if policy == PolicyType.FIXED:
            predicted_action = self.fixed_policy.evaluate(current_rf, timestamp)
            fallback_action = None
        elif policy == PolicyType.UNGATED:
            predicted_res = self.ungated_policy.evaluate(
                canonical_state=canonical_state,
                forecast_results=forecast_results,
                threshold_config=self.threshold_config,
            )
            predicted_action = predicted_res.decision
            fallback_action = None
            reason_codes.append(EvaluationReasonCode.UNGATED_AI_ACTION_ALLOWED)
        elif policy == PolicyType.GATED:
            gated_res = self.gated_policy.evaluate(
                raw_record=eval_raw,
                required_fields=required_fields,
                tag=tag,
                shell_name=shell_name,
                canonical_state=canonical_state,
                forecast_results=forecast_results,
                feature_vector=eval_feat,
                threshold_config=self.threshold_config,
            )
            gated_dec_res = gated_res["decision_result"]
            rel_res = gated_res["reliability_result"]
            gate_status = rel_res.status
            fallback_used = gated_res["fallback_used"]
            
            if fallback_used:
                predicted_action = DecisionState.ABSTAIN
                fallback_action = gated_res["action"]
                reason_codes.append(EvaluationReasonCode.FALLBACK_TO_FIXED_POLICY)
            else:
                predicted_action = gated_dec_res.decision
                fallback_action = None
                reason_codes.append(EvaluationReasonCode.GATED_AI_ACTION_ALLOWED)

        reason_codes.append(EvaluationReasonCode.GROUND_TRUTH_EVALUATED_ONLY)

        actual_outcome_str = "HIGH_FOULING" if actual_future_rf >= threshold else "LOW_FOULING"

        outcome_cls = classify_outcome(
            policy=policy,
            predicted_action=predicted_action,
            fallback_action=fallback_action if policy == PolicyType.GATED and fallback_used else None,
            actual_future_rf=actual_future_rf,
            threshold=threshold,
            gate_status=gate_status,
        )

        eval_id = f"m7_eval_{int(timestamp)}_{policy.value}_{condition.value}_{uuid.uuid4().hex[:6]}"

        return PolicyEvaluationResult(
            evaluation_id=eval_id,
            timestamp=timestamp,
            exchanger_id=exchanger_id,
            condition=condition,
            policy=policy,
            current_rf=current_rf,
            forecast_horizon=horizon,
            predicted_rf=primary_pred if policy != PolicyType.FIXED else None,
            actual_future_rf=actual_future_rf,
            threshold=threshold,
            predicted_action=predicted_action,
            actual_outcome=actual_outcome_str,
            gate_status=gate_status,
            fallback_used=fallback_used,
            outcome_class=outcome_cls,
            reason_codes=reason_codes,
            provenance=EvaluationProvenance(),
        )

    def run_experiment_suite(
        self,
        eval_instances: List[Dict[str, Any]],
    ) -> Tuple[Dict[str, List[PolicyEvaluationResult]], Dict[str, PolicySummaryResult]]:
        """
        Runs complete M7 experiment across all instances for 3 policies and 2 conditions.
        Returns detailed results and summary metrics.
        """
        all_results: Dict[str, List[PolicyEvaluationResult]] = {}
        summaries: Dict[str, PolicySummaryResult] = {}

        config_ref = {
            "exchanger_id": self.threshold_config.exchanger_id,
            "threshold_rf": self.threshold_config.rf_threshold,
            "planning_horizon_hours": self.threshold_config.planning_horizon_hours,
            "perturbation_shift_factor": self.perturber.shift_factor,
        }

        for cond in [EvaluationCondition.SUPPORTED, EvaluationCondition.SHIFTED]:
            for pol in [PolicyType.FIXED, PolicyType.UNGATED, PolicyType.GATED]:
                key = f"{cond.value}_{pol.value}"
                results_list = []
                for inst in eval_instances:
                    res = self.evaluate_single_instance(
                        raw_record=inst["raw_record"],
                        required_fields=inst["required_fields"],
                        tag=inst["tag"],
                        shell_name=inst["shell_name"],
                        canonical_state=inst["canonical_state"],
                        forecast_results=inst["forecast_results"],
                        feature_vector=inst.get("feature_vector"),
                        actual_future_rf=inst["actual_future_rf"],
                        condition=cond,
                        policy=pol,
                    )
                    results_list.append(res)

                all_results[key] = results_list
                summaries[key] = compute_summary_metrics(
                    results=results_list,
                    condition=cond,
                    policy=pol,
                    config_ref=config_ref,
                )

        return all_results, summaries
