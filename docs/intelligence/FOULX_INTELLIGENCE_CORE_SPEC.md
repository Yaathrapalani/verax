# FOUL-X Intelligence Core Specification (Stage 6)

## Purpose
The Stage 6 Intelligence Core transforms validated temporal engineering states into reproducible, benchmarked fouling prognoses with explicit model identity, feature lineage, temporal scope, and evaluation provenance.

## Scope
Stage 6 produces the forecast (`FoulingPrognosis`) for operational horizons (1h, 6h, 24h).
It does NOT determine whether the forecast is trustworthy enough to influence maintenance (Stage 7 Reliability Gate) nor does it perform causal explanation/diagnosis (Stage 8).

## Key Components
- **FoulingState**: Time-aware asset state capturing derived fouling resistance \(R_{f,\text{derived}}\), recent trends, and growth rates.
- **FoulingPrognosis**: Canonical prognosis container carrying prediction values, baseline references, model lineage, feature lineage, and training/evaluation scopes.
- **IntelligenceEngine**: Unified forecasting engine orchestrating baseline models (Persistence, RecentTrend) and benchmark predictive models (Ridge).
- **ModelEvaluator**: Independent evaluation harness supporting model comparison on validation splits.

## Principles
1. **Temporal Integrity**: Only data at or prior to origin timestamp \(T\) is consumed.
2. **Explicit Fallbacks**: Missing inputs return `INSUFFICIENT_HISTORY` or `INVALID_INPUT` without silent imputation.
3. **No Overclaims**: Aggregate \(R_f\) forecasts make zero claim regarding physical mechanism, and uncertainty is tagged as `NOT_IMPLEMENTED`.
