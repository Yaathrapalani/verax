# Document Extraction Specification

**Version:** 1.0.0  
**Status:** Approved Stage 1 Baseline  

---

## Engineering Document Extraction

Extracts equipment tags, line numbers, and design parameters from PDFs, PFDs, P&IDs, and datasheets.

### Provenance & Truth States
- **Directly Visible Tag (e.g. `E-101`):** Extracted with `TruthState.OBSERVED` state.
- **Unverified Tag (e.g. `E-999`):** Extracted with `TruthState.UNRESOLVED` and `asset_type="UNRESOLVED"` state.
- **Anti-Hallucination Rule:** Unknown equipment tags are NEVER automatically declared to be heat exchangers without supporting explicit evidence.
