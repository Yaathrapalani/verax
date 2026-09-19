# Heat Exchanger Engineering Specification

**Version:** 1.0.0  
**Status:** Approved Stage 5 Baseline  

---

## Heat Exchanger Domain Integration

`HeatExchangerStateBuilder` projects state at $T$ by referencing frozen FOUL-X M2 physics outputs ($Q$, $\text{LMTD}$, $\text{UA}$, $R_f$) without modifying scientific equations or baseline thresholds.

### Hydraulic Unavailability
Pressure telemetry ($\Delta P$) is NOT present in the dataset. Hydraulic state returns `UNAVAILABLE` with reason:
`REQUIRED_PRESSURE_EVIDENCE_NOT_AVAILABLE`
