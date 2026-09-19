# Investigation Failure Modes Specification

## Failure Modes & Handling
1. **INSUFFICIENT_EVIDENCE**: Returned when evidence count is zero or missing prerequisite history.
2. **CONFLICTING_EVIDENCE**: Returned when opposing evidence exists. Preserves both without silent resolution.
3. **TEMPORAL_INVESTIGATION_VIOLATION**: Raised if evidence timestamp \(> T\).
4. **SCENARIO_EXECUTION_ERROR**: Raised if Stage 9 scenario simulation is attempted within Stage 8.
