# Tabular Mapping Specification

**Version:** 1.0.0  
**Status:** Approved Stage 1 Baseline  

---

## Tabular Telemetry Mapping

PLANT-X ingests telemetry from CSV, XLSX, JSON, and Parquet files conservatively.

### Key Rules
1. **Header Inspection:** Column names are inspected for candidate parameter names and embedded units (e.g. `T_in (C)`).
2. **Numeric Safety:** Non-numeric entries are skipped or flagged as malformed without crashing.
3. **No Automatic Measurement Guessing:** Columns are mapped to candidate measurements with provenance; unverified columns are assigned `stream_id="UNASSIGNED"`.
