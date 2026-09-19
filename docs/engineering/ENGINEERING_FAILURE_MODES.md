# Engineering Core Failure Modes

**Version:** 1.0.0  
**Status:** Approved Stage 5 Baseline  

---

## Failure Modes & Handling

| Defect / Violation | Handling | Status Result |
| :--- | :--- | :--- |
| **Missing Required Input** | `CalculationRegistry` check | `INSUFFICIENT_DATA` / `UNAVAILABLE` |
| **Missing / Unknown Unit** | `QuantityStatus` check | `UNIT_UNRESOLVED` |
| **Dimensional Incompatibility**| Dimensional check | `DIMENSION_MISMATCH` |
| **Physical Bound Violation** | Constraint evaluation | `INCONSISTENT` |
| **Unavailable Pressure Data** | Sensor availability check | `REQUIRED_PRESSURE_EVIDENCE_NOT_AVAILABLE` |
