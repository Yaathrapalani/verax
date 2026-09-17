# FOUL-X M2 Physics State Specification & Sign-Convention Audit

**Specification Version:** 1.0  
**Calculation Engine Version:** 1.0  
**State Schema Version:** 1.0  
**Date:** 2026-09-16  

---

## 1. Physics Sign-Convention Audit

| Stream / Parameter | Stream Assignment | Direction / Temperature Logic | Heat Duty Sign Convention |
|---|---|---|---|
| **Tube Side** | Cold Fluid (Crude Oil) | $T_{tube,out} > T_{tube,in}$ | $Q_{tube} = \dot{m}_{tube} \cdot C_{p,tube} \cdot (T_{tube,out} - T_{tube,in}) \ge 0$ |
| **Shell Side** | Hot Fluid (Product Stream) | $T_{shell,in} > T_{shell,out}$ | $Q_{shell} = \dot{m}_{shell} \cdot C_{p,shell} \cdot (T_{shell,in} - T_{shell,out}) \ge 0$ |

---

## 2. LMTD Flow Arrangement & Definitions

- **Flow Arrangement Assumption**: Counter-current heat exchanger flow is assumed for all 5 preheat exchangers (E01 to E05).
  > [!NOTE]
  > This is an explicit modeling assumption for this synthetic physics dataset and is NOT presented as an independently verified plant fact.

- **Temperature Difference Definitions**:
  $$\Delta T_1 = T_{shell,in} - T_{tube,out}$$
  $$\Delta T_2 = T_{shell,out} - T_{tube,in}$$

- **LMTD Calculation**:
  $$LMTD = \frac{\Delta T_1 - \Delta T_2}{\ln(\Delta T_1 / \Delta T_2)}$$
  If $\Delta T_1 \le 0$ or $\Delta T_2 \le 0$, the logarithmic argument is invalid for counter-current heat exchange; $LMTD$ is marked as `None` and primary status set to `INVALID_LMTD`.

---

## 3. Thermal Balance Error Discrepancy Metric

Both $Q_{tube}$ (heat absorbed) and $Q_{shell}$ (heat released) are non-negative ($Q \ge 0$). The relative thermal discrepancy metric is defined as:
$$\text{thermal\_balance\_error} = \frac{|Q_{tube} - Q_{shell}|}{\max(Q_{tube}, Q_{shell})}$$

---

## 4. Fouling Target Terminology

The derived target quantity is named:
`R_f_derived` (or `derived fouling-resistance proxy`).
It is defined as:
$$R_{f, derived} = \frac{1}{UA} - \frac{1}{UA_{clean\_reference}}$$
It MUST NOT be called "measured true fouling resistance" because it is a physics-derived proxy calculated from measured temperatures and flow rates.

---

## 5. Exchanger-Specific $UA_{clean}$ References

Each exchanger has its own independent reference baseline computed strictly from initial training data ($t \le 100$ hours):
- `UA_clean_E01` (Heavy Naphtha) $\approx 207,061.2$ W/K
- `UA_clean_E02` (Kero) $\approx 213,435.9$ W/K
- `UA_clean_E03` (Light Diesel) $\approx 218,414.6$ W/K
- `UA_clean_E04` (LVGO) $\approx 220,519.3$ W/K
- `UA_clean_E05` (Heavy Diesel) $\approx 215,565.4$ W/K

No single global $UA_{clean}$ value is used across exchangers.

---

## 6. Validity Semantics & Failure Reasons

- **Validity Definition**: `VALID` indicates that a calculation passed all implemented numerical and physical domain sanity checks. It does NOT mean the physical plant state is proven correct or optimal.
- **Multiple Invalidity Reasons**: A state records both a `primary_status` (Enum) and a list of all detected failure/warning reasons (`reasons: List[str]`).

---

## 7. No Silent Repair Policy

- No silent clipping of values.
- No replacing `NaN` or `Inf` with zeros.
- No silent repair of invalid $LMTD$ or zero flows. Invalid inputs explicitly set `primary_status != VALID` and record failure reasons.
