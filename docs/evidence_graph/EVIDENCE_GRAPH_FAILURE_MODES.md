# Evidence Graph Failure Modes

**Version:** 1.0.0  
**Status:** Approved Stage 4 Baseline  

---

## Failure Modes & Handling

| Defect / Violation | Detection Mechanism | Graph Result |
| :--- | :--- | :--- |
| **Future Data Leakage ($t > T$)** | `trace_backward` | `TemporalLineageViolationError` Exception |
| **Missing Upstream Evidence** | `trace_backward` | `PARTIALLY_SUPPORTED` |
| **Conflicting Source Claims** | `CONTRADICTS` Edge | `SufficiencyStatus.CONTRADICTED` |
| **Unresolved Entity Link** | `TruthState.UNRESOLVED` | `SufficiencyStatus.UNRESOLVED` |
| **Missing Node Endpoint** | `validate_graph()` | Validation Error Message |
