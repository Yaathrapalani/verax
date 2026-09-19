# Sampling Characterization Specification

**Version:** 1.0.0  
**Status:** Approved Stage 2 Baseline  

---

## Sampling Regime Classification

Sampling behavior is classified via coefficient of variation ($CV = \sigma_{\Delta t} / \mu_{\Delta t}$) across observed timestamp deltas:
- **`REGULAR`**: $CV < 0.1$
- **`IRREGULAR`**: $0.1 \le CV \le 1.5$
- **`BURSTY`**: $CV > 1.5$
- **`INSUFFICIENT_HISTORY`**: Observation count $< 3$.
- **`UNKNOWN`**: Undefined cadence or zero time span.
