# FOUL-X M4.0 — Causal Fouling Model Specification

## 1. Mathematical Objective
Forecast derived fouling resistance $R_{f,\text{derived}}(t+h)$ for $h \in \{1\text{h}, 6\text{h}, 24\text{h}\}$:

$$Y(t+h) = R_{f,\text{derived}}(t+h)$$

using ONLY historical features $X(t) \in \mathcal{F}_t$ observed at or before timestamp $t$.

## 2. Model Architecture
- **Base Algorithm**: Ridge Regression (`sklearn.linear_model.Ridge`)
- **Scaling**: `sklearn.preprocessing.StandardScaler` fit strictly on Training observations ($t \le 44,799$) and applied unchanged to Validation and Test splits.
- **Regularization Hyperparameter Tuning**: $\alpha \in \{10^{-4}, 10^{-3}, 10^{-2}, 0.1, 1.0, 10.0, 100.0, 1000.0\}$ optimized per exchanger and horizon $h$ on Validation split.

## 3. Causal Feature Matrix ($X(t)$)
1. **Current State Variables at $t$**: $R_{f,\text{derived}}$, $UA$, $\text{LMTD}$, $Q_{\text{tube}}$, $Q_{\text{shell}}$, $\text{thermal\_discrepancy\_rel}$.
2. **Operating Parameters at $t$**: Crude composition ($\text{Crude\_API}$, $\text{Crude\_TAN}$, $\text{Crude\_Chlorides}$), temperatures ($T_{\text{tube,in}}$, $T_{\text{tube,out}}$, $T_{\text{shell,in}}$, $T_{\text{shell,out}}$), mass flow rates ($m_{\text{tube}}$, $m_{\text{shell}}$).
3. **Instantaneous Trends**: 1-hour delta ($\Delta R_{f,1\text{h}}$) and 24-hour rate of change.
4. **Causal Rolling Statistics over Windows $W \in \{6\text{h}, 24\text{h}, 72\text{h}, 168\text{h}\}$**:
   - Rolling Mean: $\frac{1}{W} \sum_{i=0}^{W-1} R_f(t-i)$
   - Rolling Standard Deviation: $\sigma_W(R_f)$
   - Rolling Min & Max
   - Delta & Slope over window $W$

## 4. Chronological Split & Leakage Controls
- **Training**: Indices $0 \dots 44,799$ ($70\%$)
- **Validation**: Indices $44,800 \dots 54,399$ ($15\%$)
- **Test**: Indices $54,400 \dots 63,999$ ($15\%$)

### Leakage Controls
1. Features for row $t$ use only index rows $\le t$.
2. Target $y(t) = R_{f,\text{derived}}(t+h)$ is strictly aligned without leaking into $X(t)$.
3. Scaler `mean_` and `var_` are computed strictly on Training split.
