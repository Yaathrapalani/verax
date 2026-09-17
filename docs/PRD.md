# FOUL-X Product Requirements Document

## 1. Product
FOUL-X — decision support for heat-exchanger fouling and cleaning timing.

## 2. Primary user
The immediate user is an operations/maintenance engineer who needs to understand current fouling, likely progression, forecast reliability, and whether a cleaning recommendation is sufficiently supported.

## 3. Problem
Fixed cleaning schedules do not adapt to changing fouling behaviour. A predictive system can help, but an unreliable forecast should not automatically override an established maintenance policy.

## 4. Goals
- Estimate current fouling state from available operating data.
- Forecast fouling progression and remaining operating period where supported by data.
- Explicitly assess forecast reliability.
- Recommend CLEAN/WAIT only when the reliability gate passes.
- Abstain with an auditable reason when reliability is insufficient.
- Fall back to a fixed policy.
- Demonstrate whether gating improves decision safety versus ungated prediction.
- Provide a production-compatible architecture without claiming plant approval.

## 5. Non-goals
- Automatic control of plant equipment.
- Claiming universal validity across exchanger types/plants.
- Claiming novel fouling forecasting algorithms.
- Claiming real industrial validation without evidence.
- Building a full CMMS/DCS/SCADA integration during the hackathon.

## 6. MVP requirements
### FR-01 Data ingestion
Accept a documented historian-like schema and validate records.
### FR-02 State estimation
Produce a documented fouling-related state from available measurements.
### FR-03 Forecast
Produce a baseline forecast before any deep temporal model.
### FR-04 Cleaning-cycle handling
Represent cleaning events and reset/transition logic explicitly.
### FR-05 Reliability gate
Check data completeness, physical consistency, historical/regime support, and optionally forecast uncertainty/calibration when implemented.
### FR-06 Abstention
Return a machine-readable abstain state with reasons.
### FR-07 Fallback
Return the fixed-policy action when the gate fails.
### FR-08 Decision support
When the gate passes, produce an advisory cleaning-window recommendation using documented assumptions.
### FR-09 Evaluation
Compare fixed, ungated, and gated policies on held-out time periods including perturbed/OOD cases.
### FR-10 Auditability
Record input timestamp/cycle, model version, gate checks, decision, reason, and configuration.

## 7. Non-functional requirements
- deterministic/reproducible experiments
- modular model interfaces
- unit and integration tests
- no hidden network dependency for core inference
- macOS-compatible development/runtime path
- containerized deployment path
- clear logging and error states
- graceful handling of missing/invalid inputs

## 8. Success metrics
Primary:
- reduction in harmful recommendations relative to ungated forecasting
- gate behaviour on perturbed/OOD segments
- abstention quality
- useful recommendation rate

Secondary:
- forecast error
- interval/calibration quality if implemented
- decision/cost consequence where supported
- latency
- reproducibility

## 9. User experience
The dashboard must answer five questions immediately:
1. What is happening now?
2. What happens next?
3. Can I trust the forecast?
4. What should I do?
5. Why?

Every recommendation is advisory and requires engineer approval.
