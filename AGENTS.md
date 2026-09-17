# FOUL-X Engineering Constitution

## Mission
Build a scientifically defensible, real-time-capable prototype for heat-exchanger fouling prognosis and maintenance decision support.

## Core thesis
FOUL-X estimates fouling, forecasts its progression, evaluates forecast reliability, and either recommends a cleaning window or abstains and falls back to the existing fixed policy.

## Research contribution boundary
The contribution is the fouling-specific reject-option/reliability-gate decision layer plus explicit fixed-policy fallback. Fouling prediction, RUL, uncertainty quantification, physics-informed modeling, and cleaning optimization are established components and must not be presented as individually novel.

## Non-negotiable rules
1. Never fabricate plant data, maintenance records, industrial interviews, benchmarks, endorsements, or savings.
2. Clearly label public, synthetic, simulated, and real plant data.
3. Never silently invent physical equations, thresholds, sensor ranges, units, or economic assumptions. Put assumptions in `docs/assumptions.md`.
4. Prevent temporal leakage. Train/test splits must respect time and cleaning cycles.
5. Every production-looking recommendation is advisory and requires human approval.
6. The fixed-policy fallback must be explicit, observable, testable, and never hidden inside model code.
7. The gate must be independently testable from the forecast model.
8. Every experiment must be reproducible from a documented configuration and seed.
9. Prefer simple baselines before deep learning.
10. Do not optimize for accuracy alone; evaluate decision safety, abstention, calibration, and cost relative to a fixed policy.
11. Do not modify unrelated modules to make a test pass.
12. Keep interfaces stable and typed where practical.
13. No network/plant integration is assumed unless explicitly configured.
14. Never call the hackathon prototype production-approved.

## Development order
M0 Foundation → M1 Data Contract → M2 Physics/State → M3 Baseline → M4 Temporal Model → M5 Reliability Gate → M6 Decision → M7 Scientific Comparison → M8 Dashboard → M9 Deployment → M10 Red Team → M11 Release.

## Definition of done for each milestone
- implementation is isolated to the intended scope
- tests cover meaningful logic
- documentation is updated
- assumptions are recorded
- no fabricated evidence is introduced
- a reproducible command exists
- git checkpoint is created before the next milestone

## Preferred workflow
Read the relevant docs first. Make the smallest coherent change. Run tests. Report changed files, evidence, assumptions, tests, and unresolved issues. Stop at the requested milestone.
