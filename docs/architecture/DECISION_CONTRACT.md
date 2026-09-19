# Decision Contract Specification

**Version:** 1.0.0  
**Status:** Approved Stage 0 Baseline  

---

## Generic Decision Object Contract

PLANT-X standardizes decision entities across all process intelligence modules.

### Attributes
- **`decision_id`**: Unique identifier.
- **`asset_id`**: Target equipment item.
- **`evidence_ids`**: List of supporting measurement and event IDs.
- **`prediction_id`**: Forecast prediction reference.
- **`uncertainty_id`**: Uncertainty bound reference.
- **`recommendation`**: Action string (`OPERATE`, `CLEANING_REVIEW`, `ABSTAIN`).
- **`abstention`**: Boolean flag indicating if AI prediction was withheld by reliability gate.
- **`reason`**: Explanation for decision state or abstention.
- **`human_approval`**: Sign-off object (`HumanApproval`).
- **`outcome`**: Post-operational evaluation (`Outcome`).
