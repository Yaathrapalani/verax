# FOUL-X M1-B Temporal & Entity Split Design

**Design Date:** 2026-09-16  
**Status:** Approved Design (Execution deferred to M3/M4)  

## Split Strategy Overview
To prevent temporal leakage, future-to-past information flow, and entity/exchanger leakage, FOUL-X adopts a strictly chronological time-series split across all 5 heat exchangers operating in series.

## Chronological Partitioning

| Split Segment | Time Range (`Time_hr`) | Row Count | Percentage | Primary Purpose |
|---|---|---|---|---|
| **Train Set** | $0 \le t \le 44,799$ | 44,800 | 70.0% | Model training and state estimator calibration. |
| **Validation Set** | $44,800 \le t \le 54,399$ | 9,600 | 15.0% | Hyperparameter tuning and reliability gate validation. |
| **Test Set** | $54,400 \le t \le 63,999$ | 9,600 | 15.0% | Out-of-sample evaluation of gated decision policy. |

## Leakage Prevention Rules
1. **Strict Chronological Ordering**: Time splits respect $t_{train} < t_{val} < t_{test}$. Random k-fold cross-validation is strictly forbidden for time-series evaluation.
2. **Entity/Exchanger Co-evaluation**: All 5 exchangers (E01 to E05) are evaluated synchronously at each timestep $t$, preserving the physical crude preheat train stream flow order ($E01 \rightarrow E02 \rightarrow E03 \rightarrow E04 \rightarrow E05$).
3. **No Temporal Feature Contamination**: Preprocessing scaling/normalization parameters (mean, std, min, max) must be computed exclusively on the Train Set and applied deterministically to Validation and Test Sets.
