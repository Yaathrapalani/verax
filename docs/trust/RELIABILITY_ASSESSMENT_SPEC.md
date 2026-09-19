# Reliability Assessment Specification

## Overview
`ReliabilityAssessment` is the canonical Stage 7 result object.

## Fields
- `asset_id`: Heat exchanger tag.
- `timestamp`: Evaluation timestamp \(T\).
- `forecast_reference`: Evaluated Stage 6 prognosis details.
- `data_status`: Data trust check state (`PASS` / `FAIL`).
- `sensor_status`: Sensor validity state (`PASS` / `FAIL` / `UNKNOWN`).
- `physics_status`: Physical consistency state (`PASS` / `FAIL`).
- `regime_status`: Historical regime support state (`SUPPORTED` / `UNSUPPORTED`).
- `uncertainty_status`: Uncertainty state.
- `overall_state`: `TRUSTED`, `CONDITIONALLY_TRUSTED`, `ABSTAIN`, or `UNAVAILABLE`.
- `decision_permission`: Boolean flag governing whether downstream decision engines may use the prediction.
- `fallback_policy`: Active explicit fallback policy (`FIXED_TIME_BASED_MAINTENANCE_POLICY`).
- `reason_codes`: Deterministically ordered machine-readable failure reason codes.
