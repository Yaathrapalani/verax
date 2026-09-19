# Imputation Governance Specification

**Version:** 1.0.0  
**Status:** Approved Stage 2 Baseline  

---

## Controlled Imputation Governance

Imputation is strictly disabled by default (`imputation_enabled: False`).

### Requirements when Enabled by Policy
- `is_imputed = True` flag explicitly set.
- Original raw value preserved.
- `imputation_method` (e.g. `FORWARD_FILL`) recorded.
- Provenance lineage preserved.
- Unpermitted imputation attempts leave value as `None`.
