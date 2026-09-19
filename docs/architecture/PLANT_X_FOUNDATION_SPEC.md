# PLANT-X Foundation Specification

**Version:** 1.0.0  
**Status:** Approved Stage 0 Baseline  
**System:** PLANT-X — Evidence-Gated Industrial Intelligence  

---

## 1. Domain Entities & Canonical Schemas

PLANT-X establishes a universal domain model for industrial process assets, measurements, predictions, decisions, and evidence.

### Core Entities
1. **Plant:** Top-level facility container.
2. **Asset:** Individual equipment item (e.g., Shell & Tube Exchanger `HX-101`).
3. **Stream:** Process fluid piping flow connecting assets.
4. **Measurement:** Sensor tag readings (e.g., Temperature, Pressure, Flow).
5. **Material:** Chemical fluid specifications and properties.
6. **Event & MaintenanceEvent:** Operational interventions and cleaning records.
7. **Geometry:** Equipment design parameters (Surface Area, Tube Count, Diameter).
8. **Constraint:** Safety and operating envelope limits.
9. **Evidence:** Raw documentation, sensor historian payload, or operator log.
10. **Computation:** Derived algorithm executions (e.g. M2 physics $R_f$).
11. **Prediction:** Model forecasts (e.g. M4 Causal Ridge prognosis).
12. **Uncertainty:** Quantified error bands and confidence bounds.
13. **Hypothesis & Investigation:** Root cause analysis structures.
14. **Scenario:** Simulated operating condition hypotheses.
15. **Decision:** Actionable advice (Clean Now / Defer / Abstain).
16. **HumanApproval:** Mandatory safety sign-off record.
17. **Outcome:** Recorded actual maintenance costs and downtime.
18. **ModelContract & ModelVersion:** Universal interface for machine learning models.
19. **SimulationContract:** Adapter contract for Aspen/DWSIM integrations.
20. **Provenance:** Comprehensive lineage tracker.
