# Evidence Graph Audit Report

## Traceability Audit
1. **TRACE WHY**: Clicking "Trace Why" in the Evidence Drawer opens `EvidenceOverlay.tsx`, presenting the causal lineage chain (Sensors $\rightarrow$ Thermal Discrepancy $\rightarrow$ Fouling Growth).
2. **TRACE IMPACT**: Displays downstream impact on preheat train fuel consumption and throughput constraints.
3. **Backend Lineage Connection**:
   - Evidence nodes reference deterministic dataset hashes.
   - UI nodes visually map to Stage 4 Evidence Graph schemas.
4. **Visual Integrity**: Node links and evidence chains are cleanly formatted; no decorative-only unlinked badges are present.
