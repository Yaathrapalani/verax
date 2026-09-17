# FOUL-X M3 Forecasting Problem Specification

**Specification Version:** 1.0  
**Date:** 2026-09-16  

## 1. Target Definition
The forecasting target is defined as:
$$Y(t+h) = R_{f, derived}(t+h)$$
where $R_{f, derived}$ is the derived fouling resistance proxy calculated from thermodynamic energy balance and heat exchanger conductance ($UA$).

## 2. Candidate Horizons & Selection Protocol
- **Candidate Horizons**: $h \in \{1\text{h}, 6\text{h}, 24\text{h}, 72\text{h}, 168\text{h}\}$.
- **Design Selection Protocol**: Horizon suitability and model selection decisions are performed EXCLUSIVELY using Training ($t \le 44,799\text{h}$) and Validation ($44,800\text{h} \le t \le 54,399\text{h}$) set evaluations.
- **Test Set Isolation**: The Test Set ($t \ge 54,400\text{h}$) remains completely untouched during baseline design selection.

## 3. Causal Feature Context Window
- Features at forecast origin $t$ are strictly constrained to historical observations $X(t) \in [t-W, t]$.
- Observations from $t+1 \dots t+h$ are strictly forbidden from participating in feature inputs.

## 4. Baseline Models
1. **Persistence Baseline**: $\hat{R}_f(t+h) = R_f(t)$.
2. **Recent-Trend Baseline**: $\hat{R}_f(t+h) = R_f(t) + h \cdot \text{slope}_{t-W:t}$ ($W=24\text{h}$).
3. **Causal Moving Average Baseline**: $\hat{R}_f(t+h) = \text{mean}(R_f(t-W+1 \dots t))$ ($W=24\text{h}$).

## 5. Common Result Interface (`ForecastResult`)
All baseline predictions output a standardized schema:
- `exchanger_id`, `timestamp`, `horizon_hours`, `prediction`, `target_definition`, `input_window_start`, `input_window_end`, `status`, `unavailable_reasons`, `provenance`, `method`, `model_version`.
