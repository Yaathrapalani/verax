# Canonical Model Specification

**Version:** 1.0.0  
**Status:** Approved Stage 0 Baseline  

---

## Domain Entity Schemas

PLANT-X standardizes domain schemas under `src/plantx/domain/entities.py`.

### Schema Summary
- **Plant**: Facility definition with truth state and provenance.
- **Asset**: Equipment unit with constraints and geometry links.
- **Stream**: Process flow links between assets.
- **Measurement**: Sensor reading with parameter name, value, and unit validation.
- **Decision**: Advisory recommendation (OPERATE, CLEANING_REVIEW, ABSTAIN) with abstention reasoning.
- **HumanApproval**: Sign-off record for advisory actions.
