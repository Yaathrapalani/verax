# Evidence Manifest Specification

**Version:** 1.0.0  
**Status:** Approved Stage 1 Baseline  

---

## Immutable Evidence Manifest

Every source evidence file ingested into PLANT-X generates an immutable `EvidenceManifest`.

### Manifest Attributes
- **`source_id`**: Unique UUID/string identifier.
- **`filename`**: Original file name.
- **`source_type`**: Classification (`Telemetry`, `Engineering`, `Operational`, `Visual`).
- **`format`**: File format extension.
- **`size_bytes`**: Exact file size in bytes.
- **`checksum_sha256`**: SHA-256 hash of original file content.
- **`ingested_at`**: ISO 8601 timestamp.
- **`parser_name`**: Parser class utilized.
- **`parser_version`**: Parser implementation version.
- **`status`**: Ingestion status (`INGESTED`, `PARSED`, `FAILED`, `UNSUPPORTED_FORMAT`).
- **`coverage`**: Extraction coverage score (0.0 to 1.0).
- **`training_eligible`**: Governance invariant — `False` by default.
- **`provenance`**: Complete provenance lineage object.
