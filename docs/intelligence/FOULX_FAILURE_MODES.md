# FOUL-X Failure Modes Specification

## Failure Modes & Handling
1. **INSUFFICIENT_HISTORY**:
   - Cause: Context window depth < 24 hours.
   - Handling: Return status = `INSUFFICIENT_HISTORY`, prediction = `None`. Zero silent imputation.

2. **INVALID_INPUT**:
   - Cause: Requested timestamp out of dataset bounds or invalid parameters.
   - Handling: Return status = `INVALID_INPUT`, prediction = `None`.

3. **UNAVAILABLE**:
   - Cause: Unfitted model or sensor outage.
   - Handling: Return status = `UNAVAILABLE`, prediction = `None`.

4. **TEMPORAL_LEAKAGE**:
   - Cause: Observation timestamp \(> T\).
   - Handling: Hard exception (`CausalTemporalLeakageError`) or `INVALID_INPUT` status.
