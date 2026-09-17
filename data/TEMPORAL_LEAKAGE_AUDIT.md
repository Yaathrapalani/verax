# FOUL-X M3 Temporal Leakage Audit

**Audit Date:** 2026-09-16  
**Status:** Audit Complete — Zero Leakage Verified  

## 1. Feature Window Causal Isolation
- **Rule**: Feature window $X(t)$ uses ONLY observations $\le t$.
- **Verification**: `get_causal_window(series, current_time, window_hours)` returns slice $[t - W + 1, t]$.
- **Leakage Prevention**: No future values ($t+1 \dots t+h$) are allowed inside $X(t)$.

## 2. Parameter Fitting Isolation
- **Rule**: Baseline parameters (e.g., $UA_{clean}$, trend slopes) are fitted exclusively on training data ($t \le 44,799\text{h}$).
- **Verification**: No validation or test set statistics participate in fitting baselines or normalization scales.

## 3. Test Set Preservation
- **Rule**: The Test Set ($54,400\text{h} \le t \le 63,999\text{h}$) is kept completely untouched during baseline design and horizon selection.
- **Verification**: Horizon analysis was conducted strictly on Validation Set timesteps.

## 4. Invalid State Handling
- **Rule**: If input state or current $R_f$ is invalid/missing, baselines MUST NOT silently impute or forward-fill.
- **Verification**: Baselines return `status = UNAVAILABLE` or `INVALID_CURRENT_STATE` with explicit reasons.
