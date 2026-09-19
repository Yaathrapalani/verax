# Stage 2 — Temporal Failure Modes

**Version:** 1.0.0  
**Status:** Approved Stage 2 Baseline  

---

## Failure Modes & Usability Consequences

| Defect / Condition | Detection Mechanism | Usability State |
| :--- | :--- | :--- |
| **Out-of-Order Timestamps** | `validate_timestamp_sequence` | `UNAVAILABLE` |
| **Duplicate Timestamps** | `validate_timestamp_sequence` | `UNAVAILABLE` |
| **Insufficient History (< 3 points)** | `characterize_sampling` | `INSUFFICIENT_HISTORY` |
| **Stale Observation (Age > Max)** | `evaluate_freshness` | `CONDITIONALLY_USABLE` |
| **Missing Observation** | Missing value check | `CONDITIONALLY_USABLE` |
| **Future Data Leakage ($t > T$)** | `align_causally(strict_causal=True)` | `CausalTemporalLeakageError` Exception |
