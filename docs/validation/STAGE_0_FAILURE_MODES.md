# Stage 0 — Structured Failure Modes

**Version:** 1.0.0  
**Status:** Approved Stage 0 Baseline  

---

## Explicit Failure Modes & Error Types

PLANT-X explicitly categorizes structural and operational data failures into structured error types. No silent repair is performed.

| Error Type | Trigger Condition | Consequence |
| :--- | :--- | :--- |
| `MISSING_IDENTIFIER` | Entity identifier is empty or None | Validation failure |
| `DUPLICATE_IDENTITY` | Multiple assets share the same asset_id | Validation failure |
| `INVALID_UNIT` | Unit not in engineering registry | Validation failure |
| `IMPOSSIBLE_VALUE` | Physical bounds violated (e.g. T < 0 K) | Validation failure |
| `MISSING_PROVENANCE` | Derived or measured value lacks provenance | Validation failure |
| `INVALID_RELATIONSHIP` | Edge points to non-existent graph node | Exception raised |
| `ORPHAN_MEASUREMENT` | Measurement links to non-existent stream | Validation failure |
| `CONTRADICTORY_TRUTH_STATE` | OBSERVED state paired with CALCULATION source | Validation failure |
