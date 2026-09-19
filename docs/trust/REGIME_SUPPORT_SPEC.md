# Regime Support Specification

## Methodology
Uses train-only feature space statistics (\(t \le 44,799\)) to determine whether an operating vector \(X(t)\) lies within historical support.
Max normalized Z-score deviation exceeding threshold (\(Z > 4.0\)) triggers `REGIME_UNSUPPORTED` and forces system abstention (`ABSTAIN`).
