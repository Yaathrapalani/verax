# FOUL-X M3.1 Baseline Evidence Completeness Audit

**Audit Date:** 2026-09-16  
**Status:** Complete  

---

## 1. Target Scale Analysis & Summary Statistics

The target quantity $R_{f, derived}$ is a thermodynamic derived fouling resistance proxy ($m^2 \cdot K/W$).

| Exchanger ID | Exchanger Name | Min ($m^2 \cdot K/W$) | Max ($m^2 \cdot K/W$) | Mean ($m^2 \cdot K/W$) | Median ($m^2 \cdot K/W$) | Std ($\sigma$) ($m^2 \cdot K/W$) | IQR ($m^2 \cdot K/W$) |
|---|---|---|---|---|---|---|---|
| **E01** | Heavy Naphtha | $-3.18 \times 10^{-7}$ | $4.02 \times 10^{-7}$ | $7.63 \times 10^{-9}$ | $7.28 \times 10^{-9}$ | $1.06 \times 10^{-7}$ | $1.43 \times 10^{-7}$ |
| **E02** | Kero | $-3.39 \times 10^{-7}$ | $3.28 \times 10^{-7}$ | $-3.25 \times 10^{-8}$ | $-3.26 \times 10^{-8}$ | $1.05 \times 10^{-7}$ | $1.41 \times 10^{-7}$ |
| **E03** | Light Diesel | $-3.13 \times 10^{-7}$ | $3.36 \times 10^{-7}$ | $1.29 \times 10^{-8}$ | $1.31 \times 10^{-8}$ | $1.05 \times 10^{-7}$ | $1.42 \times 10^{-7}$ |
| **E04** | LVGO | $-3.06 \times 10^{-7}$ | $3.62 \times 10^{-7}$ | $-1.12 \times 10^{-8}$ | $-1.12 \times 10^{-8}$ | $1.05 \times 10^{-7}$ | $1.42 \times 10^{-7}$ |
| **E05** | Heavy Diesel | $-3.24 \times 10^{-7}$ | $3.65 \times 10^{-7}$ | $-1.47 \times 10^{-8}$ | $-1.47 \times 10^{-8}$ | $1.05 \times 10^{-7}$ | $1.42 \times 10^{-7}$ |

- **Primary Target Scale Definition**: Standard Deviation ($\sigma \approx 1.05 \times 10^{-7}\text{ m}^2 \cdot K/W$).
- **Normalized MAE Formula**: $\text{NMAE} = \frac{\text{MAE}}{\sigma_{R_f}}$.

---

## 2. Percentage Metric Audit (sMAPE Analysis)

- **Finding**: At short horizons ($h=1\text{h}$), Persistence achieves $R^2 = 0.821$ and absolute $\text{MAE} = 3.57 \times 10^{-8}$, representing high predictive accuracy relative to overall variance. However, sMAPE returns **45.2%**.
- **Root Cause**: $R_{f, derived}$ is centered near zero ($10^{-8}\text{ to }10^{-7}\text{ m}^2 \cdot K/W$) with small fluctuations. In sMAPE:
  $$\text{sMAPE} = \frac{2 |y - \hat{y}|}{|y| + |\hat{y}| + \epsilon}$$
  When $y \approx 0$, small absolute errors yield disproportionately large percentage ratios, rendering sMAPE unstable.
- **Audit Recommendation**: sMAPE is classified as **NOT RECOMMENDED FOR PRIMARY TARGET EVALUATION**. Primary metric evaluation MUST rely on absolute MAE and Normalized MAE ($\text{NMAE} = \text{MAE}/\sigma$).

---

## 3. Full Exchanger Evaluation Tables (Validation vs Test)

### Exchanger E01 (Heavy Naphtha)

| Split | Horizon | Model | MAE | NMAE ($\text{MAE}/\sigma$) | RMSE | $R^2$ | MBE | Relative Imp. (%) |
|---|---|---|---|---|---|---|---|---|
| **Validation** | 1h | Persistence | $3.57 \times 10^{-8}$ | 0.337 | $4.48 \times 10^{-8}$ | 0.821 | $5.39 \times 10^{-13}$ | Baseline (0.0%) |
| **Validation** | 1h | RecentTrend (24h) | $3.62 \times 10^{-8}$ | 0.341 | $4.55 \times 10^{-8}$ | 0.815 | $-1.52 \times 10^{-11}$ | -1.40% |
| **Validation** | 24h | Persistence | $1.12 \times 10^{-7}$ | 1.057 | $1.39 \times 10^{-7}$ | -0.735 | $1.29 \times 10^{-11}$ | Baseline (0.0%) |
| **Validation** | 24h | RecentTrend (24h) | $1.41 \times 10^{-7}$ | 1.330 | $1.76 \times 10^{-7}$ | -1.782 | $-3.65 \times 10^{-10}$ | -25.89% |
| **Test** | 1h | Persistence | $3.58 \times 10^{-8}$ | 0.338 | $4.49 \times 10^{-8}$ | 0.819 | $3.21 \times 10^{-13}$ | Baseline (0.0%) |
| **Test** | 1h | RecentTrend (24h) | $3.63 \times 10^{-8}$ | 0.342 | $4.56 \times 10^{-8}$ | 0.814 | $-1.48 \times 10^{-11}$ | -1.40% |
| **Test** | 24h | Persistence | $1.13 \times 10^{-7}$ | 1.066 | $1.40 \times 10^{-7}$ | -0.748 | $7.71 \times 10^{-12}$ | Baseline (0.0%) |

*(Complete 5-exchanger evaluation matrices across all 5 candidate horizons are archived in [`artifacts/m3/full_exchanger_baseline_results.json`](file:///Users/anush/Downloads/FOUL-X_DEV/artifacts/m3/full_exchanger_baseline_results.json)).*

---

## 4. Baseline Failure vs Horizon Limitation

- **Baseline Failure**: Linear trend extrapolation over long horizons ($h \ge 24\text{h}$) is a baseline model failure. Naive linear slope estimation amplifies high-frequency measurement noise, causing predictions to diverge ($\text{NMAE} > 1.3$, $R^2 < -1.7$).
- **Forecast Horizon Limitation**: At $h=168\text{h}$, target autocorrelation decays to near zero ($\rho_{168} \approx -0.015$). Predicting exact point values 7 days ahead with unconditioned naive models carries inherent thermodynamic uncertainty.

---

## 5. Operational Forecasting Question

> [!IMPORTANT]
> **Unresolved Design Question**: Does maintenance decision support ultimately require point prediction of $R_f(t+h)$, or prediction of whether an operational degradation threshold will be crossed within a future time window?
> 
> *Status*: Retained as an open architectural question for subsequent decision-support milestones. Point prediction of $R_{f, derived}(t+h)$ remains the official target.
