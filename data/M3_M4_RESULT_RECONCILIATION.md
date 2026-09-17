# FOUL-X M3/M4 Baseline Result Reconciliation

## 1. M3 vs M4 Persistence Baseline Results & Discrepancies

### Anomaly 1: E01 h=1h Persistence MAE Discrepancy
- **M3.1 Initial Report (`BASELINE_RESULTS.md`)**: MAE = $3.57 \times 10^{-8}\text{ m}^2 \cdot K/W$
- **M3.1 Full Analysis (`full_exchanger_baseline_results.json`)**: MAE = $6.02 \times 10^{-8}\text{ m}^2 \cdot K/W$
- **M4.0 Erroneous Initial Run**: MAE = $7.97 \times 10^{-9}\text{ m}^2 \cdot K/W$
- **M4.0 Corrected Full Run**: MAE = $6.0232 \times 10^{-8}\text{ m}^2 \cdot K/W$

#### Explanation of Root Causes
1. **M3 Initial vs Full Discrepancy**: The initial summary in `BASELINE_RESULTS.md` was evaluated on an un-aligned subsample, whereas `full_exchanger_baseline_results.json` evaluated all $N=9,600$ validation rows.
2. **M4 Initial Error**: In the first M4 run, `pers_preds_val` was aligned against un-shifted $R_f(t)$ instead of target $y(t+h) = R_f(t+h)$, effectively evaluating $R_f(t) - R_f(t) = 0$ noise residual against standard deviation rather than $R_f(t+h) - R_f(t)$.
3. **Corrected Alignment**: Fixing `pers_preds_val` to evaluate against $y(t+h) = R_f(t+h)$ yields **exact mathematical parity ($6.0232 \times 10^{-8}$)** with M3.1 full validation evaluation.

---

### Anomaly 2: Identical ~80% Improvements Across All Exchangers in M4 Initial Run
- **M4 Initial Run**: Reported identical $1.12 \times 10^{-7}$ Persistence MAE and ~80% Ridge improvement across all 5 exchangers.
- **Root Cause**: The un-aligned target indexing artifact dominated the metric calculation equally across all exchangers.
- **Corrected M4 Results**: Real target variability shows distinct, nuanced performance across exchangers:
  - **E01**: 1h: +25.42% ($4.4922 \times 10^{-8}$), 6h: +20.80% ($5.5146 \times 10^{-8}$), 24h: +23.31% ($6.7481 \times 10^{-8}$)
  - **E02**: 1h: +26.95% ($4.6872 \times 10^{-8}$), 6h: +23.65% ($5.3889 \times 10^{-8}$), 24h: +25.92% ($6.0802 \times 10^{-8}$)
  - **E03**: 1h: +27.92% ($4.8992 \times 10^{-8}$), 6h: +25.48% ($5.4078 \times 10^{-8}$), 24h: +26.32% ($5.9883 \times 10^{-8}$)
  - **E04**: 1h: +28.47% ($5.0131 \times 10^{-8}$), 6h: +25.69% ($5.3781 \times 10^{-8}$), 24h: +27.16% ($5.8108 \times 10^{-8}$)
  - **E05**: 1h: +28.64% ($5.6499 \times 10^{-8}$), 6h: +25.36% ($6.1379 \times 10^{-8}$), 24h: +26.06% ($6.5802 \times 10^{-8}$)

---

## 2. Definitive Authoritative Baseline Benchmark Table

| Exchanger | Horizon | M3 Full Pers MAE | Corrected M4 Pers MAE | Difference | Apples-to-Apples? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **E01** | 1h | 6.0232e-08 | 6.0232e-08 | 0.0000 | YES |
| **E01** | 6h | 6.9627e-08 | 6.9627e-08 | 0.0000 | YES |
| **E01** | 24h | 8.7995e-08 | 8.7995e-08 | 0.0000 | YES |
| **E02** | 1h | 6.4166e-08 | 6.4166e-08 | 0.0000 | YES |
| **E02** | 6h | 7.0584e-08 | 7.0584e-08 | 0.0000 | YES |
| **E02** | 24h | 8.2080e-08 | 8.2080e-08 | 0.0000 | YES |
| **E03** | 1h | 6.7972e-08 | 6.7972e-08 | 0.0000 | YES |
| **E03** | 6h | 7.2565e-08 | 7.2565e-08 | 0.0000 | YES |
| **E03** | 24h | 8.1273e-08 | 8.1273e-08 | 0.0000 | YES |
| **E04** | 1h | 7.0088e-08 | 7.0088e-08 | 0.0000 | YES |
| **E04** | 6h | 7.2375e-08 | 7.2375e-08 | 0.0000 | YES |
| **E04** | 24h | 7.9777e-08 | 7.9777e-08 | 0.0000 | YES |
| **E05** | 1h | 7.9174e-08 | 7.9174e-08 | 0.0000 | YES |
| **E05** | 6h | 8.2236e-08 | 8.2236e-08 | 0.0000 | YES |
| **E05** | 24h | 8.8989e-08 | 8.8989e-08 | 0.0000 | YES |
