# Conflict Handling Specification

**Version:** 1.0.0  
**Status:** Approved Stage 1 Baseline  

---

## Conflict Handling

When multiple evidence sources disagree regarding an asset property (e.g. Shell & Tube vs Plate Exchanger):

### Rules
1. **No Silent Selection:** The intake engine NEVER silently picks one claim over another.
2. **Conflict Output:** Flagged as `ResolutionStatus.CONFLICT`.
3. **Preservation:** Both source claims and their respective provenance records are preserved for operator resolution.
