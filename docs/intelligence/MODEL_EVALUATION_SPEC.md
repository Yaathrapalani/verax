# Model Evaluation Specification

## Overview
Evaluates model accuracy cleanly across operational horizons and exchangers.

## Metrics
- **MAE** (Mean Absolute Error)
- **RMSE** (Root Mean Squared Error)
- **MBE** (Mean Bias Error)
- **R²** (Coefficient of Determination)

## Data Split Boundary
- **Training**: \(t = 0 \dots 44,799\)
- **Validation**: \(t = 44,800 \dots 54,399\)
- **Test**: \(t = 54,400 \dots 63,999\)
