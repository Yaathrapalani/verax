# Forecast Contract Specification

## Overview
`ForecastContract` defines the rigorous protocol governing forecasting requests and returns.

## Contract Protocol
1. **Inputs**:
   - `asset_id`: Registered heat exchanger ID.
   - `timestamp`: Origin timestamp \(T\).
   - `horizon_hours`: Target operational horizon (\(h \in \{1, 6, 24\}\)).
   - `model_id`: Requested model family (`Persistence`, `RecentTrend`, `Ridge`).

2. **Temporal Integrity Constraints**:
   - Only observations with \(t_{\text{observed}} \le T\) are accessible.
   - Zero future target information permitted in model inputs.

3. **Status Transitions**:
   - If timestamp out of dataset bounds \(\to\) `INVALID_INPUT`.
   - If history length < 24 hours \(\to\) `INSUFFICIENT_HISTORY`.
   - If model missing or error \(\to\) `UNAVAILABLE`.
   - Otherwise \(\to\) `AVAILABLE`.
