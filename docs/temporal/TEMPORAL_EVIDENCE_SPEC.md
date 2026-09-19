# Temporal Evidence Specification

**Version:** 1.0.0  
**Status:** Approved Stage 2 Baseline  
**System:** PLANT-X — Evidence-Gated Industrial Intelligence  

---

## 1. Problem Statement & Principle
A valid physical measurement is not automatically a valid process state. Real-world telemetry exhibits missing observations, asynchronous sensor sampling, irregular frequencies, stale records, and duplicate timestamps. Naive interpolation, forward filling, or temporal repair destroys scientific validity.

PLANT-X introduces a production-grade **Temporal Evidence Layer** to evaluate timestamp integrity, sampling regularity, missingness, and freshness before evidence becomes engineering state.

### Core Principle
"A valid measurement is not automatically a valid process state."
