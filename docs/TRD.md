# FOUL-X Technical Requirements Document

## 1. System boundary
Core FOUL-X is a decision-support engine. External plant systems are represented by adapters/interfaces; no direct control of plant equipment is in scope.

## 2. Logical pipeline
```text
Historian-like input
  → schema/data validation
  → state/feature computation
  → forecast model
  → reliability gate
  → decision engine
  → audit record
  → API/dashboard
```

## 3. Components
- `data`: schema, validation, ingestion and cleaning-cycle representation
- `physics`: physically meaningful state calculations
- `features`: derived model features
- `models`: model interfaces and baseline models
- `forecasting`: temporal forecast orchestration
- `gate`: reliability/reject-option logic
- `decision`: policy, economics and fallback
- `evaluation`: leakage-safe experiments and metrics
- `app/api`: inference/service boundary
- `app/dashboard`: operator-facing visualization

## 4. Interfaces
Forecast model must expose a stable prediction interface independent of the UI and decision policy.

Reliability gate must consume forecast evidence and data/state evidence and return:
- pass/fail
- individual check results
- reasons
- evidence metadata

Decision engine must consume gate output and return:
- CLEAN / WAIT / FALLBACK / REVIEW state
- rationale
- relevant estimates
- human approval requirement

## 5. Data handling
Canonical timestamps must be explicit. Units and sensor semantics must be documented. Cleaning events must be represented as events rather than inferred silently.

## 6. Validation
All model development uses time-aware splits. Cleaning-cycle boundaries must be respected. Perturbation/OOD tests must be generated and labelled as simulated unless sourced from real operations.

## 7. Deployment direction
Target packaging:
- Python inference package
- FastAPI service
- React dashboard
- Docker Compose for local/demo deployment

Future plant deployment may add historian/OPC-UA adapters, authentication, RBAC, secure networking, observability, model registry, and plant-specific validation.

## 8. Reliability gate design
Initial checks:
1. completeness/data integrity
2. physical consistency
3. historical/regime support

Optional later check:
4. forecast uncertainty/calibration

The gate must never silently convert failure to success.
