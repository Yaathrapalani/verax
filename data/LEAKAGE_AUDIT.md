# FOUL-X M1-B Leakage Audit

**Audit Date:** 2026-09-16  
**Status:** Audit Complete (v1.1 Correction)  

## 1. True / Hidden Ground-Truth Variables Inventory
- **Ground-Truth Columns Present in Raw Dataset**: `HIDDEN_GROUND_TRUTH = 0` columns present in `data/raw/heat_exchanger_fouling_dataset.csv`.
- **Forbidden Ground-Truth Patterns for Future Datasets**: Any simulation ground-truth parameter matching `*_True` or `*_True_*` (e.g. `R_fouling_True`, `U_fouled_True`, `Q_actual_True`, `T_wall_avg_True_C`) is classified as `HIDDEN_GROUND_TRUTH`.
- **Rule**: If future datasets or simulation scripts include `*_True` or equivalent simulation-truth variables, they are strictly forbidden from inference inputs unless explicitly justified. They can only be used as target evaluation labels or hidden physics validation benchmarks.

## 2. Future Information
- **Rule**: No feature at timestamp $t$ may incorporate information from timestamp $t+k$ ($k > 0$).
- **Finding**: Rolling window features, lead/lag transforms, or future statistics must be strictly causal (backward-looking only, e.g. $[t-w, t]$).

## 3. Variables Derived from Target
- **Rule**: Any variable calculated directly using target values $R_{f}(t)$ or future $R_f(t+k)$ must not be used as an input feature.
- **Finding**: Target $R_{f, derived}$ is calculated physically from measured temperatures and flow rates ($Q_{tube}, LMTD$). The inputs to $R_{f, derived}$ ($T_{in}, T_{out}, \dot{m}$) are legitimate measured inputs, but the output $R_f$ itself is the target and cannot be fed back into features without proper time lags.

## 4. Variables Not Available at Inference Time
- **Finding**: Pressure drop ($\Delta P$), internal tube wall temperatures ($T_{wall}$), fluid viscosities, and exact tube geometry parameters are NOT present in the dataset and are classified as `NOT_AVAILABLE`. No fabricated proxies are created.

## 5. Target Leakage Prevention Rules
1. Preprocessing pipelines (e.g., scaling, normalization) must compute statistics strictly on the training set split.
2. Input feature selection validation explicitly filters out any column matching `*_True` or `*_R_fouling*`.
3. Automated unit tests fail loudly if forbidden target or ground-truth columns are detected in model input schemas.
