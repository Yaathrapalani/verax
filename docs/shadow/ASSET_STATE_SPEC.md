# Asset State Specification

**Version:** 1.0.0  
**Status:** Approved Stage 3 Baseline  

---

## Time-Aware Asset State

`AssetState` resolves equipment state at evaluation timestamp $T$.

### Fields
- `asset_id`: Canonical asset ID.
- `resolution_status`: Stage 1 resolution status (`RESOLVED`, `CANDIDATE_MATCH`, `CONFLICT`, `UNRESOLVED`).
- `truth_state`: Stage 0 truth state (`OBSERVED`, `INFERRED`, `REPRESENTATIVE`, `UNRESOLVED`).
- `measurement_bindings`: Sensor measurement links with freshness tags.
- `geometry_state`: Projection geometry with `truth_state=REPRESENTATIVE`.
- `physics_ref` / `fouling_ref` / `forecast_ref` / `reliability_ref` / `decision_ref`: Frozen FOUL-X subsystem result references.
