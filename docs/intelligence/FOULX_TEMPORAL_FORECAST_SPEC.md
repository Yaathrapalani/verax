# FOUL-X Temporal Forecast Specification

## Horizons
Primary operational forecast horizons:
- **1h**: Immediate operational tracking.
- **6h**: Shift-level maintenance planning.
- **24h**: Daily scheduling boundary.

72h and 168h horizons are evaluated only where existing M3 evidence supports reporting and are marked unvalidated for operational decision-making.

## Baseline Hierarchy
- **Model 0**: Persistence Baseline (\(\hat{R}_f(t+h) = R_f(t)\))
- **Model 1**: RecentTrend Baseline (\(\hat{R}_f(t+h) = R_f(t) + h \cdot \text{slope}(t-W:t)\))
- **Model 2**: Ridge Regression Baseline (Fitted strictly on \(t \le 44,799\))
