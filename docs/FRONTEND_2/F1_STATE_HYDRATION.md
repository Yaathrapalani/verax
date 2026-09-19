# F1 State Hydration Report

## Hydration Architecture
- `PlantStateHydrator` fetches `ReplaySnapshotDTO` from `/api/replay/snapshot` endpoint.
- Maps raw backend metrics to `PlantClientState`:
  - `physics_state` $\rightarrow$ $Q$, LMTD, $UA$, $R_f$
  - `reliability_state` $\rightarrow$ Trust Gate (`PASS` / `ABSTAIN`), check details, `REGIME_OOD` reason codes
  - `decision_state` $\rightarrow$ Decision (`ABSTAIN` / `CLEANING_REVIEW`) with human approval requirement
  - `provenance` $\rightarrow$ Dataset SHA-256 (`c8ed7d9c...4b4d9`)
