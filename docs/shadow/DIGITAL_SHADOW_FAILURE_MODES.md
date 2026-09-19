# Stage 3 — Digital Shadow Failure Modes

**Version:** 1.0.0  
**Status:** Approved Stage 3 Baseline  

---

## Failure Modes & Handling

| Defect / Ambiguity | Handling | Shadow Result |
| :--- | :--- | :--- |
| **Future Observation ($t > T$)** | `align_causally(strict_causal=True)` | `CausalTemporalLeakageError` Exception |
| **Conflicting Source Claims** | `ConservativeEntityResolver` | `ResolutionStatus.CONFLICT` + `ShadowIssue` |
| **Unresolved Equipment Tag** | Unknown tag handling | `ResolutionStatus.UNRESOLVED` + `truth_state=UNRESOLVED` |
| **Missing Sensor Data** | None value check | `truth_state=UNRESOLVED` |
| **Stale Telemetry** | Age check against policy | `freshness_status="STALE"` |
