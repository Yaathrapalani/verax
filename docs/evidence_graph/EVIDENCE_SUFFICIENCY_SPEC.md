# Evidence Sufficiency Specification

**Version:** 1.0.0  
**Status:** Approved Stage 4 Baseline  

---

## Deterministic Evidence Sufficiency

Sufficiency is computed strictly from graph structural conditions:
- **`SUPPORTED`**: Complete lineage to root evidence sources.
- **`PARTIALLY_SUPPORTED`**: Missing upstream evidence links detected.
- **`CONTRADICTED`**: Conflicting evidence edges exist.
- **`UNRESOLVED`**: Lineage contains unresolved entity nodes.
- **`INSUFFICIENT_EVIDENCE`**: Upstream root evidence missing entirely.
