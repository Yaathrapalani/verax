# FOUL-X M1-B Physics Observability Audit

**Audit Date:** 2026-09-16  
**Status:** Audit Complete  

## Summary Matrix

| Physical Quantity | Observability Classification | Formula / Method | Notes & Constraints |
|---|---|---|---|
| **Tube Heat Duty ($Q_{tube}$)** | `CALCULABLE` | $\dot{m}_{tube} \cdot C_{p,tube} \cdot (T_{tube,out} - T_{tube,in})$ | Uses measured temperatures, mass flow, and constant $C_p$. |
| **Shell Heat Duty ($Q_{shell}$)** | `CALCULABLE` | $\dot{m}_{shell} \cdot C_{p,shell} \cdot (T_{shell,in} - T_{shell,out})$ | Uses measured shell temperatures, mass flow, and constant $C_p$. |
| **Log Mean Temp Diff ($LMTD$)** | `CALCULABLE` | $\frac{\Delta T_1 - \Delta T_2}{\ln(\Delta T_1 / \Delta T_2)}$ | Counter-current flow assumed: $\Delta T_1 = T_{s,in} - T_{t,out}$, $\Delta T_2 = T_{s,out} - T_{t,in}$. |
| **Overall Thermal Conductance ($UA$)** | `CALCULABLE` | $\frac{Q_{tube}}{LMTD}$ | Directly derived from thermal energy balance and $LMTD$. |
| **Fouling Resistance ($R_{f, derived}$)** | `CALCULABLE` | $\frac{1}{UA_{fouled}} - \frac{1}{UA_{clean}}$ | Requires clean baseline $UA_{clean}$ (e.g., initial timesteps). |
| **Heat Transfer Coeff ($U$)** | `REQUIRES ASSUMPTIONS` | $U = \frac{UA}{A}$ | Heat transfer area $A$ is NOT provided in CSV. Requires geometric assumption. |
| **Hydraulic Indicators / Pressure Drop ($\Delta P$)** | `NOT_AVAILABLE` | N/A | No pressure or differential pressure sensors in dataset. |
| **Reynolds Number ($Re$)** | `NOT_AVAILABLE` | N/A | Fluid viscosity and tube geometry (diameter, count) are NOT provided. |

## Guidance on Derived Variables
Derived physical variables ($Q, LMTD, UA, R_{f, derived}$) are **physically derived variables** and MUST NOT be silently promoted to directly measured inputs.
