# EQUIPMENT_RUNTIME_SPEC.md\n\n# STAGE 14 EQUIPMENT SIMULATION RUNTIME

## Overview
Stage 14 defines the executable equipment-level simulation layer for PLANT-X, orchestrating Stage 5 heat exchanger calculations while maintaining honest boundaries for unparameterized equipment (Pumps, Valves).

## Core Architectural Invariants
- **Simulation != Observation**: Simulated values are explicitly tagged  with complete input, parameter, and solver provenance.
- **No Fabricated Performance**: Pump hydraulics and valve Cv curves are reported as  without fake curve fitting.
- **Safety Boundary**: Advisory simulation outputs only (). Autonomous control attempts raise .
