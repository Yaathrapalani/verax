# Quantity and Unit Specification

**Version:** 1.0.0  
**Status:** Approved Stage 5 Baseline  

---

## Quantity & Unit Handling

`EngineeringQuantity` encapsulates value, units, dimension, and lineage.

### Unit Rules
- Original value & unit preserved (`original_value`, `original_unit`).
- SI conversion applied deterministically (`normalized_value`, `normalized_unit`).
- Missing unit strings are assigned `status = QuantityStatus.UNIT_UNRESOLVED` without silent guessing.
