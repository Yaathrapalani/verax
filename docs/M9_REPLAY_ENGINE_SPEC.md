# M9.0 Deterministic Industrial Replay Engine Specification

## 1. Scientific & Architectural Overview
The FOUL-X M9.0 Deterministic Replay Engine reconstructs authoritative single-source-of-truth snapshots (`ReplaySnapshot`) for historical dataset timestamps ($t \in [0, 63999] \, \text{hours}$).

```
Historical Replay Timestamp (t)
   ↓
Historical Resolver (`src/foulx/replay/resolver.py`)
   ↓ (No future data where Time_hr > t)
M2 Physics State Estimator (`process_record`)
   ↓
M4 Causal Ridge Prognosis (`RidgeFoulingForecaster`)
   ↓
M5 Reliability Gate (`ReliabilityGateEvaluator`)
   ↓
M6 Decision Engine (`DecisionEngineEvaluator`)
   ↓
ReplaySnapshot(t)
```

## 2. Replay Clock & Timestamp Boundaries
- **Replay Clock**: Deterministic discrete clock operating strictly over dataset timestamps. Wall-clock time controls only UI advance speed, never engineering values.
- **Dataset Boundaries**:
  - `TRAIN`: $t \in [0.0, 44799.0] \, \text{hours}$
  - `VALIDATION`: $t \in [44800.0, 54399.0] \, \text{hours}$
  - `TEST`: $t \in [54400.0, 63999.0] \, \text{hours}$
- **Boundary Behavior**: Out-of-range timestamp requests (e.g. $t < 0.0$ or $t > 63999.0$) trigger an explicit `ValueError` and `TIMESTAMP_OUT_OF_RANGE` reason code without silent data corruption.

## 3. Replay Snapshot Schema
Canonical `ReplaySnapshot` contains:
- `timestamp`: $t$ (Time_hr)
- `exchanger_id`: `E01`, `E02`, `E03`, `E04`, or `E05`
- `scenario_mode`: `NORMAL` or `SHIFTED`
- `raw_state_reference`: Historical raw record at $t$
- `physics_state`: Authoritative $M2$ physics state
- `forecast_state`: Authoritative $M4.0$ forecast result list (or `FORECAST_UNAVAILABLE`)
- `reliability_state`: Authoritative $M5.0$ reliability result
- `decision_state`: Authoritative $M6.0$ decision result
- `evidence_reference`: Coherent evidence lineage bundle
- `provenance`: Replay provenance & `no_future_leakage: True` invariant

## 4. Scenario Modes
1. **`NORMAL`**: Replays historical observations from raw dataset.
2. **`SHIFTED`**: Applies deterministic $M7.0$ synthetic $+6.0\sigma$ regime-shift perturbation to evaluate $M5$ OOD detection (`REGIME_OOD` -> `ABSTAIN`) and $M6$ fallback. Raw dataset file is NEVER mutated.

## 5. Strict Temporal Safety Invariants
1. At timestamp $t$, raw observations, $M2$ physics states, $M4$ forecast inputs, $M5$ reliability checks, and $M6$ decisions evaluate ONLY data where $\text{Time\_hr} \le t$.
2. Future actual ground-truth values ($R_f(t+h)$) are strictly excluded from current measurement structures.
3. Random number generators (`Math.random()`, `np.random`) are strictly forbidden in engineering replay calculations.

## 6. Generated Artifacts (`artifacts/m9/`)
- `snapshot_t44800.json`
- `snapshot_t45000.json`
- `snapshot_t54400.json`
- `shifted_snapshot_t45000.json`
- `replay_manifest.json`
