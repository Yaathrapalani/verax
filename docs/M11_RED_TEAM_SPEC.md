# FOUL-X M11.0 Red-Team & Failure-Safety Validation Specification

## Executive Summary
The M11.0 Red-Team & Failure-Safety Validation Suite provides automated, deterministic stress-testing of the FOUL-X industrial heat exchanger fouling prognosis and decision-support pipeline (M2-M10). It evaluates pipeline resilience under 10 controlled failure and perturbation scenarios without altering any scientific algorithms, physics equations, model weights, or existing artifacts.

## Architecture & Module Structure
- `src/foulx/redteam/reason_codes.py`: Enum `RedTeamScenarioCode` defining 10 scenario identifiers.
- `src/foulx/redteam/schemas.py`: Typed Pydantic models (`RedTeamScenarioResult`, `RedTeamSummary`, `RedTeamManifest`).
- `src/foulx/redteam/failure_injector.py`: In-memory data corruptor & regime-shift injector.
- `src/foulx/redteam/harness.py`: Orchestrator executing the complete pipeline against all 10 scenarios.
- `scripts/generate_m11_artifacts.py`: Reproducible generator creating JSON artifacts in `artifacts/m11/`.

## Evaluated Failure Scenarios
1. `MISSING_CRITICAL_MEASUREMENT`: Missing required temperature/pressure measurements (`T_shell_out=None`). Expected: `ABSTAIN`, `DATA_INVALID`.
2. `INVALID_SENSOR_VALUE`: Out-of-bounds physical measurement (`T_shell_in = -999.0 °C`). Expected: `ABSTAIN`, `DATA_OUT_OF_RANGE`.
3. `THERMAL_PHYSICS_INCONSISTENCY`: Violates energy balance ($T_{shell,out} > T_{shell,in}$). Expected: `ABSTAIN`, `PHYSICS_VIOLATION`.
4. `ESTABLISHED_REGIME_SHIFT`: $+6\sigma$ operational perturbation. Expected: `ABSTAIN`, `REGIME_SHIFT`.
5. `INSUFFICIENT_FORECAST_HISTORY`: Forecast history length below lag requirements ($L < 24$). Expected: `ABSTAIN`, `FORECAST_UNAVAILABLE`.
6. `FORECAST_UNAVAILABLE`: Forecast generation failure or missing model. Expected: `ABSTAIN`, `FORECAST_UNAVAILABLE`.
7. `MULTIPLE_SIMULTANEOUS_FAILURES`: Missing measurement + Out-of-bounds sensor + Thermal violation. Expected: `ABSTAIN`, multiple ordered reason codes preserved.
8. `NORMAL_SUPPORTED_CONTROL`: Baseline valid operational window. Expected: `PASS`, `OPERATE`.
9. `DETERMINISTIC_REPEATED_EXECUTION`: Identical inputs across repeated runs. Expected: 100% byte-for-byte identical output.
10. `SOURCE_DATA_IMMUTABILITY`: Verify raw dataset checksum (`c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9`). Expected: Pass.

## Non-Negotiable Safety Invariants
- **AI Action Withholding**: Whenever M5 Reliability Gate outputs `ABSTAIN`, M6 Decision Engine MUST return `ABSTAIN` or fallback to fixed policy (`OPERATE`), and MUST NEVER issue `CLEANING_REVIEW`.
- **Zero Autonomous Control**: FOUL-X recommendations remain strictly advisory. No automated valve actuation, plant trip, or shutdown signal is ever generated.
- **In-Memory Perturbation**: All stress scenarios execute on copied states in RAM. Source data files remain pristine.
