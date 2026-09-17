# FOUL-X M5.0 Reliability Gate Specification

## 1. Purpose & Scope
The M5.0 Reliability Gate provides an explicit, deterministic, and auditable reject-option layer for FOUL-X.
It evaluates whether a given prognosis forecast $Y(t+h) = R_{f,\text{derived}}(t+h)$ possesses sufficient data integrity, physical validity, and historical domain support to be permitted to influence maintenance decision support.

**SAFETY INVARIANT**: The gate emits either `PASS` or `ABSTAIN`. It does **NOT** generate cleaning recommendations, issue control commands, or perform economic optimization.

## 2. Gate Decision Workflow
```
Data Evidence (raw_record)
      ↓
Check 1: Data Completeness (DATA_INCOMPLETE)
      ↓
Check 2: Sensor/Input Validity (SENSOR_INVALID)
      ↓
Check 3: Physics Consistency (PHYSICS_INCONSISTENT)
      ↓
Check 4: Historical Regime Support (REGIME_OOD)
      ↓
RELIABILITY GATE DECISION → PASS / ABSTAIN
```

## 3. Check Definitions & Deterministic Order

| Priority | Check Name | Evaluation Target | Failure Reason Code |
| :--- | :--- | :--- | :--- |
| **1** | `DATA_COMPLETENESS` | Verifies presence of all required input fields for forecast origin $t$. | `DATA_INCOMPLETE` |
| **2** | `SENSOR_VALIDITY` | Checks for NaN, Inf, non-finite values, and configured physical domain violations. | `SENSOR_INVALID` |
| **3** | `PHYSICS_CONSISTENCY` | Consumes M2 `CanonicalExchangerState`. Fails if M2 status != `VALID`. | `PHYSICS_INCONSISTENT` |
| **4** | `REGIME_SUPPORT` | Audits feature vector Z-score against Train-only distribution ($t \le 44,799$). | `REGIME_OOD` |

### Deterministic Reason Code Order
If multiple checks fail, all applicable reason codes are emitted in strict priority order:
`[DATA_INCOMPLETE, SENSOR_INVALID, PHYSICS_INCONSISTENT, REGIME_OOD]`

## 4. Historical Regime Support Methodology
- **Scope**: Evaluates feature vector $X(t)$ distance from the Training set distribution ($t \le 44,799\text{h}$).
- **Formula**: $Z_i = \frac{|x_i - \mu_{train,i}|}{\sigma_{train,i}}$
- **Decision Rule**: If $\max_i (Z_i) > 4.0$ (configured threshold), the observation is classified as Out-Of-Domain (`REGIME_OOD`).
- **Leakage Prevention**: Feature mean $\mu_{train}$ and standard deviation $\sigma_{train}$ are fit **strictly** on the Training split.

## 5. Provenance & Auditability
Every `ReliabilityResult` contains full provenance tracing:
- Gate Schema Version (`1.0`)
- M2 Physics Schema Version (`1.0`)
- M4.0 Model Version (`1.0`)
- Raw Source Variables Consumed
- Dataset SHA-256 Checksum (`c8ed7d9c...b4d9`)

## 6. What This Gate Does NOT Prove
- This gate does not guarantee 100% real-world operational safety.
- It evaluates synthetic physics-based dataset bounds and domain support.
- It does NOT evaluate hydraulic pressure drop ($\Delta P$) or fluid viscosity ($\mu$) as those sensors do not exist in the dataset.
