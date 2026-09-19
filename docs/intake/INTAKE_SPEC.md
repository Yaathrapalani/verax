# Intake Specification

**Version:** 1.0.0  
**Status:** Approved Stage 1 Specification  
**System:** PLANT-X — Evidence-Gated Industrial Intelligence  

---

## Universal Evidence Intake Engine

PLANT-X Stage 1 establishes a production-grade evidence intake pipeline for multi-modal industrial evidence without silently guessing or fabricating physical engineering attributes.

### Pipeline Stages
1. **Source Identification:** File extension, magic bytes, and MIME inspection.
2. **Parsing:** Safe format-specific decoding (CSV, XLSX, JSON, Parquet, PDF, Visual).
3. **Extraction:** Identification of equipment tags, sensor tags, numerical telemetry, and context metadata.
4. **Normalization:** Conservative unit conversion (e.g. Celsius to Kelvin) preserving original value/unit.
5. **Validation:** Structured validation against domain bounds and unit registries.
6. **Semantic Mapping:** Mapping extracted tags to candidate domain attributes.
7. **Entity Resolution:** Conservative alias matching (`E-101` -> `HX-101`) preventing unauthorized merging of unverified tags.
8. **Canonical Integration:** Population of Stage 0 `Plant`, `Asset`, `Measurement`, and `EvidenceGraph` objects.
