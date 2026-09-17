# FOUL-X M3 Baseline Evaluation Results

**Evaluation Date:** 2026-09-16  
**Split Evaluated:** Validation Set ($44,800\text{h} \le t \le 54,399\text{h}$)  
**Target Variable:** $R_{f, derived}(t+h)$  

## Summary Results (Exchanger E01 - Heavy Naphtha)

| Horizon ($h$) | Model | MAE ($m^2 \cdot K/W$) | RMSE ($m^2 \cdot K/W$) | sMAPE (%) | $R^2$ | Relative Improvement vs Persistence (%) |
|---|---|---|---|---|---|---|
| **1h** | Persistence | $3.57 \times 10^{-8}$ | $4.48 \times 10^{-8}$ | 45.2% | 0.821 | Baseline (0.0%) |
| **1h** | RecentTrend (24h) | $3.62 \times 10^{-8}$ | $4.55 \times 10^{-8}$ | 45.9% | 0.815 | -1.40% |
| **1h** | MovingAverage (24h) | $7.12 \times 10^{-8}$ | $8.95 \times 10^{-8}$ | 90.1% | 0.280 | -99.44% |
| **6h** | Persistence | $8.24 \times 10^{-8}$ | $1.03 \times 10^{-7}$ | 88.5% | 0.054 | Baseline (0.0%) |
| **6h** | RecentTrend (24h) | $8.85 \times 10^{-8}$ | $1.11 \times 10^{-7}$ | 94.2% | -0.104 | -7.40% |
| **24h** | Persistence | $1.12 \times 10^{-7}$ | $1.39 \times 10^{-7}$ | 119.8% | -0.735 | Baseline (0.0%) |
| **24h** | RecentTrend (24h) | $1.41 \times 10^{-7}$ | $1.76 \times 10^{-7}$ | 148.2% | -1.782 | -25.89% |
| **72h** | Persistence | $1.15 \times 10^{-7}$ | $1.43 \times 10^{-7}$ | 122.5% | -0.841 | Baseline (0.0%) |
| **72h** | RecentTrend (24h) | $2.85 \times 10^{-7}$ | $3.56 \times 10^{-7}$ | 185.0% | -10.380 | -147.83% |
| **168h** | Persistence | $1.16 \times 10^{-7}$ | $1.44 \times 10^{-7}$ | 123.1% | -0.865 | Baseline (0.0%) |
| **168h** | RecentTrend (24h) | $6.12 \times 10^{-7}$ | $7.65 \times 10^{-7}$ | 198.4% | -51.870 | -427.58% |

## Operational Horizon Insights
1. **Short Horizons ($h=1\text{h}, 6\text{h}$)**: Persistence provides the strongest baseline performance ($R^2 = 0.821$ at 1h). High autocorrelation ($\rho_1 \approx 0.95$) makes current state highly informative.
2. **Medium/Long Horizons ($h \ge 24\text{h}$)**: Simple linear extrapolation (RecentTrend) suffers severe error explosion over longer horizons due to high-frequency fluctuations around noise baselines.
3. **Machine-Readable Full Results**: Complete evaluation results across all 5 exchangers are stored in [`artifacts/m3/baseline_results.json`](file:///Users/anush/Downloads/FOUL-X_DEV/artifacts/m3/baseline_results.json).
