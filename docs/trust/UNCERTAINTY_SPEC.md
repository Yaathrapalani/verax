# Uncertainty Specification

## Principles
1. Prediction \(\neq\) uncertainty.
2. Uncertainty is evaluated using statistically justified models (e.g. `GaussianProcessRegressor`).
3. Prediction intervals record `lower_bound`, `upper_bound`, `nominal_level`, `method`, `model_version`, and `calibration_status`.
4. Arbitrary heuristic confidence scores are strictly prohibited.
