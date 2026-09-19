# Contradiction Handling Specification

**Version:** 1.0.0  
**Status:** Approved Stage 4 Baseline  

---

## Contradictory Evidence Preservation

When multiple evidence sources disagree, the Evidence Graph preserves both source paths using `SUPPORTS` and `CONTRADICTS` edges without silently picking a winner.
