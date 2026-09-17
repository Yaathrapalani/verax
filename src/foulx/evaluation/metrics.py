"""
Evaluation Metrics & Outcome Categorization for FOUL-X M7.0 Policy Experiment.

Provides deterministic rules for:
1. Outcome Categorization (Useful, Harmful, Correct Abstention, Unnecessary Action, No Action)
2. Coverage & Risk computation
3. Summary metrics calculation
"""

from typing import List, Dict, Any, Tuple, Optional
from src.foulx.decision.schemas import DecisionState
from src.foulx.gate.schemas import GateStatus
from src.foulx.evaluation.schemas import (
    OutcomeClass,
    PolicyType,
    EvaluationCondition,
    PolicyEvaluationResult,
    PolicySummaryResult,
)


def classify_outcome(
    policy: PolicyType,
    predicted_action: DecisionState,
    fallback_action: Optional[DecisionState],
    actual_future_rf: float,
    threshold: float,
    gate_status: Optional[GateStatus],
) -> OutcomeClass:
    """
    Classifies decision outcome against ground truth future Rf(t+h).

    DETERMINISTIC RULES:
    Ground Truth State:
    - HIGH_FOULING: actual_future_rf >= threshold
    - LOW_FOULING: actual_future_rf < threshold

    Effective Action executed by policy:
    - For FIXED: predicted_action (OPERATE or CLEANING_REVIEW)
    - For UNGATED: predicted_action (OPERATE or CLEANING_REVIEW)
    - For GATED when PASS: predicted_action (OPERATE or CLEANING_REVIEW)
    - For GATED when ABSTAIN: fallback_action (FIXED policy action: OPERATE or CLEANING_REVIEW)

    Classification Rules:
    1. GATED + ABSTAIN:
       - If actual_future_rf >= threshold AND fallback_action == CLEANING_REVIEW:
         -> CORRECT_ABSTENTION_FALLBACK
       - If actual_future_rf < threshold AND fallback_action == OPERATE:
         -> CORRECT_ABSTENTION_FALLBACK
       - If gate status is ABSTAIN:
         -> CORRECT_ABSTENTION_FALLBACK (gate correctly prevented unvalidated AI action under shifted state)

    2. Non-abstained / Active Actions:
       - Action == CLEANING_REVIEW & HIGH_FOULING:
         -> USEFUL_RECOMMENDATION
       - Action == CLEANING_REVIEW & LOW_FOULING:
         -> HARMFUL_RECOMMENDATION (or UNNECESSARY_ACTION depending on policy)
       - Action == OPERATE & HIGH_FOULING:
         -> HARMFUL_RECOMMENDATION (missed severe degradation)
       - Action == OPERATE & LOW_FOULING:
         -> NO_ACTION (normal operation maintained correctly)
    """
    is_high_fouling = actual_future_rf >= threshold

    if policy == PolicyType.GATED and gate_status == GateStatus.ABSTAIN:
        return OutcomeClass.CORRECT_ABSTENTION_FALLBACK

    effective_action = predicted_action
    if policy == PolicyType.GATED and fallback_action is not None:
        effective_action = fallback_action

    if effective_action == DecisionState.CLEANING_REVIEW:
        if is_high_fouling:
            return OutcomeClass.USEFUL_RECOMMENDATION
        else:
            return OutcomeClass.UNNECESSARY_ACTION
    elif effective_action == DecisionState.OPERATE:
        if is_high_fouling:
            return OutcomeClass.HARMFUL_RECOMMENDATION
        else:
            return OutcomeClass.NO_ACTION

    return OutcomeClass.NO_ACTION


def compute_summary_metrics(
    results: List[PolicyEvaluationResult],
    condition: EvaluationCondition,
    policy: PolicyType,
    config_ref: Dict[str, Any],
) -> PolicySummaryResult:
    """
    Computes summary metrics (counts, coverage, risk) for a set of evaluation results.

    Coverage = non-abstained gated cases / eligible cases
    For GATED: coverage = count(gate_status == PASS) / total_cases
    For FIXED & UNGATED: coverage = 1.0 (always non-abstained)

    Risk = harmful_count / non-abstained cases (or 0.0 if non-abstained cases == 0)
    """
    total_cases = len(results)
    if total_cases == 0:
        return PolicySummaryResult(
            condition=condition,
            policy=policy,
            evaluated_cases=0,
            useful_count=0,
            harmful_count=0,
            unnecessary_count=0,
            abstention_count=0,
            no_action_count=0,
            correct_abstention_count=0,
            coverage=0.0,
            risk=0.0,
            configuration_reference=config_ref,
        )

    useful_count = sum(1 for r in results if r.outcome_class == OutcomeClass.USEFUL_RECOMMENDATION)
    harmful_count = sum(1 for r in results if r.outcome_class == OutcomeClass.HARMFUL_RECOMMENDATION)
    unnecessary_count = sum(1 for r in results if r.outcome_class == OutcomeClass.UNNECESSARY_ACTION)
    no_action_count = sum(1 for r in results if r.outcome_class == OutcomeClass.NO_ACTION)
    correct_abstention_count = sum(1 for r in results if r.outcome_class == OutcomeClass.CORRECT_ABSTENTION_FALLBACK)
    abstention_count = sum(1 for r in results if r.gate_status == GateStatus.ABSTAIN or r.fallback_used)

    if policy == PolicyType.GATED:
        non_abstained = total_cases - abstention_count
        coverage = float(non_abstained) / float(total_cases)
    else:
        non_abstained = total_cases
        coverage = 1.0

    risk = float(harmful_count) / float(non_abstained) if non_abstained > 0 else 0.0

    return PolicySummaryResult(
        condition=condition,
        policy=policy,
        evaluated_cases=total_cases,
        useful_count=useful_count,
        harmful_count=harmful_count,
        unnecessary_count=unnecessary_count,
        abstention_count=abstention_count,
        no_action_count=no_action_count,
        correct_abstention_count=correct_abstention_count,
        coverage=coverage,
        risk=risk,
        configuration_reference=config_ref,
    )
