# Trust Failure Modes Specification

## Failure Modes & Handling
1. **DATA_INCOMPLETE**: Missing required telemetry fields \(\to\) `ABSTAIN`.
2. **STALE_EVIDENCE**: Observation age exceeds threshold \(\to\) `ABSTAIN`.
3. **SENSOR_INVALID**: Sensor values out of bounds or non-finite \(\to\) `ABSTAIN`.
4. **SENSOR_UNKNOWN**: Unverified sensor status \(\to\) `ABSTAIN`.
5. **PHYSICS_INCONSISTENT**: Thermal energy balance or LMTD calculation fails \(\to\) `ABSTAIN`.
6. **REGIME_UNSUPPORTED**: Feature vector outside historical support (\(Z > 4.0\)) \(\to\) `ABSTAIN`.
7. **FORECAST_UNAVAILABLE**: Missing forecast prediction \(\to\) `ABSTAIN`.
8. **INSUFFICIENT_EVIDENCE**: Unavailable prerequisite data \(\to\) `ABSTAIN` / `UNAVAILABLE`.
