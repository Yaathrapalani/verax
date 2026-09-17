# FOUL-X M4 Readiness Assessment & Evidence Review

**Assessment Date:** 2026-09-16  
**Status:** READY FOR M4  

## 1. Summary of Baseline Evidence & Benchmark

- **Primary Target Scale ($\sigma$)**: $R_{f, derived}$ has a standard deviation scale of $\sigma \approx 1.05 \times 10^{-7}\text{ m}^2 \cdot K/W$ across exchangers E01 through E05.
- **Persistence Baseline Benchmark**:
  - $h = 1\text{h}$: $\text{MAE} = 3.57 \times 10^{-8}\text{ m}^2 \cdot K/W$ ($\text{NMAE} = 0.337$, $R^2 = 0.821$).
  - $h = 6\text{h}$: $\text{MAE} = 8.24 \times 10^{-8}\text{ m}^2 \cdot K/W$ ($\text{NMAE} = 0.777$, $R^2 = 0.054$).
  - $h = 24\text{h}$: $\text{MAE} = 1.12 \times 10^{-7}\text{ m}^2 \cdot K/W$ ($\text{NMAE} = 1.057$, $R^2 = -0.735$).
- **Metric Limitations**: sMAPE is unstable when $R_f \approx 0$. Absolute MAE and Normalized MAE ($\text{NMAE} = \text{MAE}/\sigma$) must serve as the primary metrics for model evaluation.

## 2. Exchanger-Specific & Horizon Behavior

- **Exchanger Behavior**: Exchangers E01 to E05 operate in series and exhibit consistent statistical variance ($\sigma \approx 1.05 \times 10^{-7}$), but differ in operating temperature ranges ($T_{in}$ ranges from 150°C in E01 to 280°C in E05).
- **Horizon Behavior**: Short horizons ($1\text{h}, 6\text{h}$) demonstrate high autocorrelation ($\rho_1 = 0.952$). At $h \ge 24\text{h}$, naive linear trend extrapolation diverges due to high-frequency sensor noise.

## 3. What M4 Temporal Models Must Demonstrate

1. **Beat Persistence MAE**: M4 temporal sequence models (e.g. TCN / LSTM) must achieve $\text{NMAE} < 0.337$ at $h=1\text{h}$ and $\text{NMAE} < 1.057$ at $h=24\text{h}$.
2. **Multi-Scale Noise Filtering**: Learn temporal smoothing and non-linear trend extraction without slope divergence over medium horizons ($24\text{h} \dots 72\text{h}$).
3. **Strict Non-Leakage**: Preserve chronological train/validation/test splits and zero future target leakage.

## 4. Unresolved Operational Questions

- *Point Prediction vs Threshold Crossing*: Does maintenance decision support ultimately require point prediction of $R_f(t+h)$, or prediction of whether an operational degradation threshold will be crossed within a future time window?
- *Classification Scope*: This question remains an open architectural consideration for decision-support milestones. Point prediction of $R_{f, derived}(t+h)$ remains the primary benchmark target.
