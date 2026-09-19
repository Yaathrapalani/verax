# Dimension Specification

**Version:** 1.0.0  
**Status:** Approved Stage 5 Baseline  

---

## Dimensional Categories

`DimensionCategory` supports standard physical dimensions:
- `MASS`, `TIME`, `TEMPERATURE`, `PRESSURE`
- `ENERGY`, `POWER`, `VOLUME`, `LENGTH`, `AREA`
- `MASS_FLOW`, `VOLUME_FLOW`, `ENERGY_FLOW`
- `HEAT_TRANSFER_COEFFICIENT`, `THERMAL_RESISTANCE`, `DIMENSIONLESS`

Dimensional incompatibility triggers `QuantityStatus.DIMENSION_MISMATCH`.
