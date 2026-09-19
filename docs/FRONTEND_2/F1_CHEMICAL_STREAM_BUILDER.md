# F1 Chemical Stream Builder Specification

## User Input Boundary
- User can specify: Phase (`LIQUID`, `VAPOR`, `TWO_PHASE`), Components (Water, Ethanol), Mole/Mass fractions, Temperature, Pressure, Mass flow.
- Validation: Fractions must sum to 1.0; temperature/pressure must be non-negative.
- **Honesty Barrier**: Thermodynamic properties (density, viscosity, enthalpy) remain explicitly `UNAVAILABLE` because no validated liquid property package exists in backend Stage 13.
