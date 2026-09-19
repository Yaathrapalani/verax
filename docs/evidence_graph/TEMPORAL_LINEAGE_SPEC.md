# Temporal Lineage Specification

**Version:** 1.0.0  
**Status:** Approved Stage 4 Baseline  

---

## Anti-Future Temporal Lineage Bound

`EvidenceGraphEngine.trace_backward()` strictly enforces the temporal constraint:
$$t_{\text{upstream}} \le T_{\text{target}}$$

Traversing an upstream node where $t_{\text{upstream}} > T_{\text{target}}$ raises a `TemporalLineageViolationError`. Future evidence can NEVER support a historical claim.
