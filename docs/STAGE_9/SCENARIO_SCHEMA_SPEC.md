# Scenario Schema Specification

## Schema
- `ScenarioCase`: Master case tracking `baseline_timestamp`, `scenario_type`, `parameters`, `applicability`, `baseline_state`, `scenario_state`, `results`, `impact_summary`, and `human_review_required`.
- `ScenarioParameter`: Tracks baseline vs perturbed values, units, perturbation type, and truth state (`SIMULATED`).
- `ScenarioResult`: Comparative result carrying baseline value, scenario value, delta, relative delta, unit, and applicability classification.
