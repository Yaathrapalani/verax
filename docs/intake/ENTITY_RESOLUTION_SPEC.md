# Entity Resolution Specification

**Version:** 1.0.0  
**Status:** Approved Stage 1 Baseline  

---

## Conservative Entity Resolution

`ConservativeEntityResolver` resolves raw equipment tags into canonical domain entity identifiers conservatively.

### Resolution Outputs
- **`RESOLVED`**: Explicit alias mapping match (`E-101` -> `HX-101`).
- **`CANDIDATE_MATCH`**: High-confidence candidate requiring engineering sign-off.
- **`CONFLICT`**: Disagreeing claims from different evidence sources (e.g. P&ID vs Datasheet).
- **`UNRESOLVED`**: Unknown equipment tag without alias entry.
