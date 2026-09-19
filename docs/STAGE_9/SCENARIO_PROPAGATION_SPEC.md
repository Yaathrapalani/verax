# Scenario Propagation Specification

## Architecture
Stage 9 recalculates engineering states strictly via Stage 5 `PhysicsStateEstimator` / `HeatExchangerStateBuilder`. No thermodynamic equations are duplicated inside Stage 9.
Outputs are marked with `truth_state = SIMULATED`.
