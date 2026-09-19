# Evidence Node Specification

**Version:** 1.0.0  
**Status:** Approved Stage 4 Baseline  

---

## Strongly Typed Graph Nodes

`EvidenceNodeV2` represents discrete evidence, entities, computations, or decisions in the graph.

### Node Classifications (`GraphNodeType`)
- `EVIDENCE_SOURCE`, `EVIDENCE_RECORD`, `EXTRACTED_EVIDENCE`
- `CANONICAL_ENTITY`, `MEASUREMENT`, `TEMPORAL_OBSERVATION`
- `ENGINEERING_COMPUTATION`, `MODEL_EXECUTION`, `PREDICTION`, `UNCERTAINTY`
- `HYPOTHESIS`, `INVESTIGATION`, `SCENARIO`
- `DECISION`, `HUMAN_APPROVAL`, `OUTCOME`
- `ASSUMPTION`, `CONSTRAINT`
