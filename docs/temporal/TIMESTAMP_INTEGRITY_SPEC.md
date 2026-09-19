# Timestamp Integrity Specification

**Version:** 1.0.0  
**Status:** Approved Stage 2 Baseline  

---

## Timestamp Validation

`TemporalEvidenceEngine.validate_timestamp_sequence()` checks observation sequences for temporal defects per measurement channel:
- **`VALID`**: Monotonic, unique, well-formed timestamps.
- **`OUT_OF_ORDER`**: Decreasing timestamp sequence.
- **`DUPLICATE_TIMESTAMP`**: Multiple observations sharing identical timestamps on a single channel.
- **`TEMPORAL_GAP`**: Large missing time gap exceeding expected cadence.
- **`FUTURE_LEAKAGE_ATTEMPT`**: Observation timestamp $t > T$ target evaluation time.

### Invariant
Timestamps are never silently repaired, re-ordered, or modified.
