# Evidence Graph Specification

**Version:** 1.0.0  
**Status:** Approved Stage 0 Baseline  

---

## Traceable Evidence Graph

PLANT-X requires complete backward traceability from recommendations to source evidence.

### Graph Nodes
- **`Evidence`**
- **`Calculation`**
- **`State`**
- **`Prediction`**
- **`Reliability`**
- **`Decision`**

### Directed Edges & Types
- **`SUPPORTED_BY`**: Links Decision to Evidence or Measurement.
- **`DERIVED_FROM`**: Links State/Calculation to raw sensor Evidence.
- **`PREDICTS`**: Links Prediction to Asset state.
- **`EVALUATES_RELIABILITY`**: Links Reliability Gate to Prediction.
- **`RECOMMENDS`**: Links Decision to operational maintenance action.

### Backward Lineage Traversal
Using `EvidenceGraph.trace_backward(decision_id)`, an operator can inspect the exact path of measurements and predictions that produced an advisory recommendation.
