# Model Contract Specification

**Version:** 1.0.0  
**Status:** Approved Stage 0 Baseline  

---

## Universal Model Interface

PLANT-X defines a universal model contract for machine learning, statistical, and physics-informed models.

### Standard Attributes
- **`model_id`**: Unique identifier for the model family.
- **`model_version`**: Version tag and git commit hash.
- **`training_data_reference`**: Reference URI/checksum of training split.
- **`feature_version`**: Feature extraction configuration version.
- **`training_window`**: Historical timestamp boundaries used for training.
- **`validation_window`**: Historical timestamp boundaries used for tuning.
- **`test_window`**: Holdout evaluation timestamp bounds.
- **`applicability`**: Explicit domain applicability constraints.
- **`limitations`**: Known out-of-distribution failure modes and boundary bounds.
- **`provenance`**: Complete lineage documentation.
