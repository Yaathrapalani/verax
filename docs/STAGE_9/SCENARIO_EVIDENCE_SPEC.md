# Scenario Evidence Specification

## Evidence Graph Extension
Scenario cases attach to Stage 4 Evidence Graph using node type `Scenario` and `truth_state = "SIMULATED"`. Edge `DERIVED_FROM` connects baseline observation nodes to scenario nodes.
Scenario outputs never masquerade as plant observations.
