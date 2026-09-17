# FOUL-X M6.0 Decision Engine Specification

## 1. Purpose & Scope
The M6.0 Decision Engine is a deterministic engineering decision-support layer for FOUL-X.
It converts current derived fouling state ($R_{f,\text{derived}}$), prognosis forecast ($R_f(t+h)$), M5 Reliability Gate decision (`PASS` or `ABSTAIN`), and explicitly configured decision parameters into one of three canonical decision states:
1. `OPERATE`
2. `CLEANING_REVIEW`
3. `ABSTAIN`

**CRITICAL SAFETY INVARIANTS**:
- The Decision Engine provides **Decision Support ONLY**, not autonomous control.
- It does **NOT** issue plant control commands, automatic shutdowns, or execute cleaning actions.
- `human_approval_required = True` is a mandatory provenance invariant.
- **Reliability Propagation Invariant**: If M5 Reliability Gate returns `ABSTAIN`, M6 **MUST** return `ABSTAIN`. There is **NO** pathway for an M5 `ABSTAIN` to produce `CLEANING_REVIEW` or `OPERATE`.

## 2. Decision Logic & Threshold Crossing Method
Decision logic evaluates whether predicted $R_{f,\text{derived}}(t+h)$ reaches or exceeds an explicitly configured site/process-dependent decision threshold $R_{f,\text{threshold}}$ within a configured planning horizon (e.g. $h \le 24\text{h}$).

```
M5 Reliability Status == PASS?
      ├── NO (ABSTAIN) ──► Decision: ABSTAIN (Reason: RELIABILITY_ABSTAIN)
      └── YES (PASS)
            └── Forecast R_f(t+h) >= R_f,threshold within Planning Horizon?
                  ├── YES ──► Decision: CLEANING_REVIEW (Reason: THRESHOLD_REACHED)
                  └── NO  ──► Decision: OPERATE (Reason: THRESHOLD_NOT_REACHED)
```

## 3. Decision States & Semantics

| Decision State | Semantics & Meaning | Action Guidance |
| :--- | :--- | :--- |
| **`OPERATE`** | Forecast trajectory remains strictly below $R_{f,\text{threshold}}$ within planning horizon AND M5 Reliability Gate status is `PASS`. | Continue normal thermal monitoring. |
| **`CLEANING_REVIEW`** | Forecast trajectory reaches/exceeds $R_{f,\text{threshold}}$ within planning horizon AND M5 Reliability Gate status is `PASS`. | Flag asset for **engineering review**. Human approval MANDATORY. |
| **`ABSTAIN`** | M5 Reliability Gate status is `ABSTAIN` OR required input signals are missing/invalid. | Withhold forecast from decision support. Existing fixed maintenance policy remains active. |

## 4. Reason Codes & Deterministic Order

1. `RELIABILITY_ABSTAIN` (Highest Precedence)
2. `FORECAST_UNAVAILABLE`
3. `CURRENT_STATE_UNAVAILABLE`
4. `INVALID_THRESHOLD`
5. `THRESHOLD_REACHED`
6. `THRESHOLD_NOT_REACHED`

## 5. What M6 Does NOT Prove
- M6 is **NOT** economic cleaning optimization (no cost functions or fuel penalty calculations are evaluated).
- M6 does **NOT** compute an exact physically optimal cleaning schedule.
- M6 does **NOT** issue autonomous control commands.

## 6. Provenance & Auditability
Every `DecisionResult` records:
- Decision Version (`1.0`)
- Gate Version (`1.0`)
- Model Version (`1.0`)
- Physics Schema Version (`1.0`)
- Mandatory Human Approval Flag (`True`)
