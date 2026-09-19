# Missingness Specification

**Version:** 1.0.0  
**Status:** Approved Stage 2 Baseline  

---

## Missingness Taxonomy

Missing values are explicitly categorized rather than reduced to plain NaNs:
- **`NOT_OBSERVED`**: Parameter not recorded at timestamp.
- **`SENSOR_OFFLINE`**: Explicit sensor offline status flag.
- **`COMMUNICATION_LOSS`**: Historian connection dropout.
- **`INVALID_VALUE`**: Out-of-bounds or non-finite physical reading.
- **`PARSER_MISSING`**: Field skipped during document intake.
- **`OUT_OF_RANGE`**: Transducer range clipping.
- **`UNKNOWN`**: Cause unverified.
