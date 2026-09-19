# Traceability Specification

**Version:** 1.0.0  
**Status:** Approved Stage 4 Baseline  

---

## Computational Lineage APIs

### 1. `explain_claim(claim_id)` — TRACE WHY
Constructs a backward lineage path detailing exact upstream measurements, physics calculations, model executions, assumptions, and source files supporting a target claim.

### 2. `impact_analysis(node_id)` — TRACE IMPACT
Constructs a forward lineage path identifying downstream computations, predictions, decisions, human approvals, and operational outcomes that depend on a selected node.
