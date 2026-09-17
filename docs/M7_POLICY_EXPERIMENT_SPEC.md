# M7.0 Policy Experiment Specification: Fixed vs Ungated vs Gated Maintenance Policies

## 1. Scientific Question
Does reliability gating (M5) reduce harmful or unsupported AI-assisted maintenance recommendations under operating regime shifts while retaining useful recommendations under historically supported operating conditions?

## 2. Hypothesis
> **Central Hypothesis**: Reliability gating can reduce harmful or unsupported AI-assisted recommendations under shifted conditions while retaining useful recommendations under supported conditions.

*Note: This experiment is strictly designed to be capable of falsifying this hypothesis.*

## 3. Policy Definitions
1. **Policy 1 — FIXED (`FIXED`)**: Configured fixed-policy baseline. Evaluates action solely based on current observed fouling resistance proxy $R_{f,\text{derived}}(t)$ against threshold $R_{f,\text{threshold}}$. Does not use AI forecasts or M5 reliability gate.
2. **Policy 2 — UNGATED (`UNGATED`)**: AI-assisted decision without reliability gating. Passes M4 causal Ridge forecast $R_f(t+h)$ directly into M6 decision engine, bypassing M5 reliability checks.
3. **Policy 3 — GATED (`GATED`)**: Authoritative reliability-gated AI policy. Evaluates M5 Reliability Gate first:
   - If M5 == `PASS`: Execute M6 AI-assisted decision.
   - If M5 == `ABSTAIN`: Abort AI recommendation and fall back strictly to Policy 1 (`FIXED`).

## 4. Fallback Mechanism
Whenever M5 Reliability Gate returns `ABSTAIN`, the `GATED` policy emits `predicted_action = ABSTAIN` with `fallback_used = True` and executes the configured `FIXED` policy rule.

## 5. Decision Target & Evaluation Ground Truth
- Target Horizon: $h = 24$ hours.
- Decision Threshold: $R_{f,\text{threshold}} = 1.5 \times 10^{-7} \, \text{m}^2 \cdot \text{K} / \text{W}$.
- Ground Truth: Actual observed fouling resistance $R_{f,\text{derived}}(t+h)$ occurring at $t+h$.
- **Strict Leakage Invariant**: Ground truth $R_{f,\text{derived}}(t+h)$ is strictly evaluation-only and is NEVER passed into M4 forecaster or M5 gate inputs.

## 6. Deterministic Outcome Categorization
- `USEFUL_RECOMMENDATION`: Policy executed `CLEANING_REVIEW` and ground truth $R_f(t+h) \ge R_{f,\text{threshold}}$ (True Positive).
- `HARMFUL_RECOMMENDATION`: Policy executed `OPERATE` when ground truth $R_f(t+h) \ge R_{f,\text{threshold}}$ (False Negative / missed severe degradation).
- `UNNECESSARY_ACTION`: Policy executed `CLEANING_REVIEW` when ground truth $R_f(t+h) < R_{f,\text{threshold}}$ (False Positive / unnecessary intervention).
- `NO_ACTION`: Policy executed `OPERATE` when ground truth $R_f(t+h) < R_{f,\text{threshold}}$ (True Negative / normal operation).
- `CORRECT_ABSTENTION_FALLBACK`: M5 Gate emitted `ABSTAIN` under unvalidated or shifted operating state, preventing unvalidated AI recommendation and falling back to `FIXED`.

## 7. Supported vs Shifted Conditions
- **Condition A (`SUPPORTED`)**: Held-out test set split ($t \in [54400, 63999]$) within historical operating support.
- **Condition B (`SHIFTED`)**: Synthetic regime-shift stress test applying deterministic shift factors (+6.0 std offset) to current process variables ($T_{\text{in}}$, $m_{\text{dot}}$) to push operating features outside historical training support ($t \le 44799$).

## 8. Coverage & Risk Metrics
- $\text{Coverage} = \frac{\text{Non-abstained Gated Cases}}{\text{Total Eligible Cases}}$
- $\text{Risk} = \frac{\text{Harmful Recommendations}}{\text{Non-abstained Cases}}$

## 9. Leakage Prevention Audit
1. Test split ($t \in [54400, 63999]$) is strictly chronological and isolated from training.
2. Model weights and hyperparameters are frozen. No retraining or threshold tuning on test split.
3. Raw dataset SHA-256 remains untouched.
4. Future ground truth $R_f(t+h)$ is used exclusively for evaluation scoring.

## 10. Boundary & No-Economic-Claim Invariant
No monetary savings, financial ROI, or economic cost reductions are claimed. Validated monetary cost parameters do not exist in the dataset.
