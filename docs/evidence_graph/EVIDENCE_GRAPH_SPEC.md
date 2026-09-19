# Evidence Graph Specification

**Version:** 1.0.0  
**Status:** Approved Stage 4 Baseline  
**System:** PLANT-X — Evidence-Gated Industrial Intelligence  

---

## 1. Problem & Purpose
The Evidence Graph makes every important PLANT-X claim computationally and evidentially traceable back to the source evidence, transformations, assumptions, models, uncertainty, decisions, human approvals, and eventual outcomes that produced or influenced it.

### Fundamental Questions Answered
1. **TRACE WHY:** "Why did PLANT-X produce this claim, prediction, recommendation, or decision?"
2. **TRACE IMPACT:** "What downstream states, predictions, recommendations, or decisions depend on this evidence?"

### Canonical Lineage Sequence
$$\text{SOURCE} \rightarrow \text{RAW EVIDENCE} \rightarrow \text{EXTRACTED EVIDENCE} \rightarrow \text{CANONICAL ENTITY} \rightarrow \text{TEMPORAL STATE} \rightarrow \text{COMPUTATION} \rightarrow \text{MODEL} \rightarrow \text{UNCERTAINTY} \rightarrow \text{HYPOTHESIS} \rightarrow \text{DECISION} \rightarrow \text{HUMAN APPROVAL} \rightarrow \text{OUTCOME}$$
