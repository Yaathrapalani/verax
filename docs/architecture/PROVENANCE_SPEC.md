# Provenance Specification

**Version:** 1.0.0  
**Status:** Approved Stage 0 Baseline  

---

## Provenance Model

Every derived, calculated, or sensed data entity in PLANT-X must carry a traceable provenance lineage record.

### Provenance Attributes
- **`provenance_id`**: Unique UUID/string for the evidence record.
- **`provenance_type`**: Source classification (`DOCUMENT`, `HISTORIAN`, `SENSOR`, `OPERATOR`, `CALCULATION`, `MODEL`, `SIMULATION`, `MANUAL_MAPPING`, `REPRESENTATIVE_TEMPLATE`).
- **`source_reference`**: Sensor tag, URI, table name, or raw dataset file path.
- **`agent_id`**: Identifier of system process, user, script, or model.
- **`timestamp`**: ISO 8601 creation or sensing timestamp.
- **`transformation_applied`**: Description of mathematical/processing transformation.
- **`upstream_provenance_ids`**: Parent provenance identifiers establishing complete evidence lineage.
