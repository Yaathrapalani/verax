# Scenario Validation Specification

## Rules
1. Perturbation magnitudes are strictly validated against prototype scenario bounds.
2. Out-of-bound perturbations raise `UnsupportedPerturbationError`. Silent clamping is strictly forbidden.
3. Every parameter perturbation requires explicit units and truth states (`SIMULATED`).
