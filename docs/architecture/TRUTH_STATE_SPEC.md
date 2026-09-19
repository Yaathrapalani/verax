# Truth State Specification

**Version:** 1.0.0  
**Status:** Approved Stage 0 Baseline  

---

## Truth States

PLANT-X mandates explicit truth states for all domain entities, variables, measurements, and geometry attributes. Silent guessing or hidden data imputation is strictly forbidden.

### Enumerated States
1. **`OBSERVED`**: Direct physical measurement from calibrated sensor telemetry or verified manual entry.
2. **`INFERRED`**: Derived parameter calculated via physics models (e.g., M2 $R_f$) or machine learning (M4 Ridge forecast). Must link to calculation provenance.
3. **`REPRESENTATIVE`**: Template or default engineering parameters (e.g., assumed design clean heat transfer coefficient $U_{clean}$).
4. **`UNRESOLVED`**: Missing, ambiguous, or uncalibrated plant parameters requiring engineering resolution.

---

## Non-Negotiable Rules
- `UNKNOWN` must **NEVER** be converted to `INFERRED`.
- `REPRESENTATIVE` must **NEVER** be converted to `OBSERVED`.
- Missing values must **NEVER** be silently guessed or auto-filled.
