# Unit Normalization Specification

**Version:** 1.0.0  
**Status:** Approved Stage 1 Baseline  

---

## Unit Normalization Engine

`UnitNormalizer` converts detected engineering units into canonical SI units conservatively.

### Output Standard
- **Original Value & Unit:** Preserved (`original_value`, `original_unit`).
- **Normalized Value & Unit:** Populated (`normalized_value`, `normalized_unit="K"`).
- **Conversion Method:** Recorded (`conversion_method="CONVERT_C_TO_K"`).
- **Ambiguous Units:** Converted to `UNIT_UNRESOLVED` state without silent guessing.
