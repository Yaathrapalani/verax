# DECISION_SCHEMA_SPEC.md

# STAGE 10 DOCUMENTATION SPECIFICATIONS

## DECISION_ENGINE_SPEC.md
The Stage 10 Decision Intelligence Engine (`src/plantx/decision/engine.py`) aggregates engineering context (Stage 5), prognoses (Stage 6), trust & selective prediction (Stage 7), investigation cases (Stage 8), and counterfactual scenarios (Stage 9). It performs decision support without autonomous control or automated cleaning execution.

## DECISION_SCHEMA_SPEC.md
Canonical schemas (`src/plantx/decision/schemas.py`) define `DecisionCase`, `DecisionOption`, `TotalCostModel`, `CostComponent`, `ConsequenceItem`, and recommendation status enums.

## DECISION_OPTION_SPEC.md
Defines the five initial candidate options: `D1: CONTINUE_OPERATION`, `D2: CLEANING_REVIEW`, `D3: SCHEDULED_CLEANING`, `D4: INVESTIGATE_BEFORE_CLEANING`, and `D5: DEFER_DECISION`.

## COST_MODEL_SPEC.md
Specifies `C_total = C_clean + C_downtime + C_energy + C_production_loss + C_risk`. Values are provided exclusively via explicit site inputs; missing values yield `UNAVAILABLE` and prohibit fake cost estimation.

## CONSEQUENCE_MODEL_SPEC.md
Qualitative consequence mapping (`src/plantx/decision/consequence_model.py`) categorizes known and unknown consequences per candidate decision option without inventing arbitrary numerical probabilities.

## DECISION_CONSTRAINT_SPEC.md
Evaluates mandatory human engineering approval, reliability gate status, and site economic completeness boundaries (`src/plantx/decision/constraints.py`).

## DECISION_COMPARISON_SPEC.md
Provides comparative overview between the deterministic M6 baseline (`OPERATE`, `CLEANING_REVIEW`, `ABSTAIN`) and candidate Stage 10 decision options.

## DECISION_PROVENANCE_SPEC.md
Enforces full lineage tracking via `Provenance` records attached to every decision case, cost component, and consequence item.

## DECISION_EVIDENCE_SPEC.md
Links Stage 10 `DecisionCase` instances back to the Stage 4 `EvidenceGraph` via `DecisionEvidenceBridge` using `EvidenceEdgeType.RECOMMENDS`.

## DECISION_FAILURE_MODES.md
Documents failure modes including missing economic inputs, temporal violations, trust gate abstention, and raw dataset mutation.

## FOULX_DECISION_SPEC.md
Describes how FOUL-X degradation forecasts inform candidate decision options while preserving M6 baseline decision logic.

## HUMAN_APPROVAL_BOUNDARY_SPEC.md
Establishes the non-negotiable principle that Stage 10 is strictly advisory (`human_review_required = True`). Autonomous plant control raises `AutonomousControlViolationError`.

## ECONOMIC_ASSUMPTION_SPEC.md
Documents the strict rule prohibiting fabricated economic parameters (cleaning cost, downtime cost, energy price, production loss, risk cost).

## STAGE_10_VALIDATION.md
Validates Stage 10 implementation against 34 comprehensive killer tests covering cost models, trust integration, investigation/scenario bridges, determinism, and safety boundaries.

## STAGE_10_READINESS.md
Confirms Stage 10 system readiness, backend test suite pass rate (297/297), frontend production build pass, and dataset SHA-256 immutability.

## STAGE_10_FINAL_REPORT.md
Final milestone report detailing Stage 10 Decision Intelligence implementation, test results, and formal GO decision.
