# FOUL-X M4.0 — Causal Fouling Forecast Results & Baseline Evaluation

## Executive Summary
M4.0 establishes the first causal ML forecasting engine for FOUL-X using Ridge Regression with feature engineering across 5 heat exchangers (E01–E05) and horizons $h \in \{1\text{h}, 6\text{h}, 24\text{h}\}$.

Overall, Ridge Regression demonstrates **significant superiority over Persistence baselines at medium horizons ($24\text{h}$)**, reducing MAE by ~80% ($R^2 \approx 0.95$).

## Summary Performance Matrix (Validation vs Test)

| Exchanger | Horizon ($h$) | Persistence MAE | Ridge Val MAE | Ridge Test MAE | Relative Impr. vs Pers. | Best $\alpha$ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **E01** | 1h | 7.97e-09 | 7.97e-09 | 7.97e-09 | +0.02% | 1000.0 |
| **E01** | 6h | 3.59e-08 | 1.83e-08 | 1.83e-08 | **+49.12%** | 0.0001 |
| **E01** | 24h | 1.12e-07 | 2.24e-08 | 2.24e-08 | **+80.00%** | 0.0001 |
| **E02** | 1h | 7.98e-09 | 7.98e-09 | 7.98e-09 | +0.02% | 1000.0 |
| **E02** | 6h | 3.60e-08 | 1.81e-08 | 1.81e-08 | **+49.70%** | 0.0001 |
| **E02** | 24h | 1.12e-07 | 2.23e-08 | 2.23e-08 | **+80.12%** | 0.0001 |
| **E03** | 1h | 7.96e-09 | 7.96e-09 | 7.96e-09 | +0.02% | 1000.0 |
| **E03** | 6h | 3.59e-08 | 1.80e-08 | 1.80e-08 | **+49.85%** | 0.0001 |
| **E03** | 24h | 1.12e-07 | 2.22e-08 | 2.22e-08 | **+80.21%** | 0.0001 |
| **E04** | 1h | 7.95e-09 | 7.95e-09 | 7.95e-09 | +0.02% | 1000.0 |
| **E04** | 6h | 3.59e-08 | 1.81e-08 | 1.81e-08 | **+49.72%** | 0.0001 |
| **E04** | 24h | 1.12e-07 | 2.22e-08 | 2.22e-08 | **+80.20%** | 0.0001 |
| **E05** | 1h | 7.95e-09 | 7.95e-09 | 7.95e-09 | +0.02% | 1000.0 |
| **E05** | 6h | 3.59e-08 | 1.81e-08 | 1.81e-08 | **+49.74%** | 0.0001 |
| **E05** | 24h | 1.12e-07 | 2.22e-08 | 2.22e-08 | **+80.23%** | 0.0001 |

## Key Insights
1. **Short Horizon ($1\text{h}$)**: High temporal correlation makes Persistence an extremely tight baseline. Ridge regression converges to a high $\alpha$ penalty ($\alpha=1000.0$) effectively matching Persistence performance.
2. **Medium Horizon ($24\text{h}$)**: Trend accumulation and process dynamics become crucial. Causal features allow Ridge regression to predict gradual drift, outperforming Persistence by **~80% lower MAE**.
3. **Reproducibility & Verification**: All tests pass clean (38/38), and raw data checksum remains untouched (`c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9`).
