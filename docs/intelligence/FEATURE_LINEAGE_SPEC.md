# Feature Lineage Specification

## Hierarchy
```
Forecast (FoulingPrognosis)
  ↓
Model (Ridge / RecentTrend / Persistence)
  ↓
Feature Vector
  ↓
FoulingState
  ↓
EngineeringState
  ↓
DigitalShadowSnapshot
  ↓
TemporalObservation
  ↓
Source (Universal Evidence Intake)
```

Every forecast object references its causal inputs and can be traced backward via the Stage 4 Evidence Graph.
