# Lineage Specification

**Version:** 1.0.0  
**Status:** Approved Stage 4 Baseline  

---

## Lineage Path & Sufficiency

`LineagePath` encapsulates a deterministic graph traversal path between a claim and its supporting root evidence.

### Sufficiency Statuses (`SufficiencyStatus`)
- **`SUPPORTED`**: Path complete; all nodes backed by evidence.
- **`PARTIALLY_SUPPORTED`**: Broken upstream evidence links detected.
- **`CONTRADICTED`**: Explicit contradictory evidence edges exist.
- **`UNRESOLVED`**: Lineage contains unresolved entity nodes.
- **`INSUFFICIENT_EVIDENCE`**: Upstream root evidence missing entirely.
