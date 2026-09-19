# Thermal Reconciliation Specification

**Version:** 1.0.0  
**Status:** Approved Stage 5 Baseline  

---

## Thermal Reconciliation

Reconciles $Q_{\text{tube}}$ and $Q_{\text{shell}}$ by computing relative discrepancies. Discrepancies exceeding physical tolerance trigger `INCONSISTENT` status without averaging or silently picking one stream.
