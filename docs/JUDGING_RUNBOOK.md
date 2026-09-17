# PLANT-X / FOUL-X Judging Runbook & Defense Guide

## 1. 30-Second Elevator Pitch
**PLANT-X** is an industrial process-intelligence platform, and **FOUL-X** is its first validated vertical for heat-exchanger fouling prognosis and decision support. FOUL-X does not treat every AI prediction as actionable: it introduces a domain-specific **Reliability Gate (M5)** that evaluates Data Completeness, Sensor Validity, Physics Consistency, and Historical Regime Support. If any reliability check fails, the system **ABSTAINS**, withholding AI recommendation and cleanly falling back to fixed plant maintenance policies.

---

## 2. 2-Minute Key Feature Demo Sequence
1. **Landing & Process Topology**: Point out the representative crude preheat train flow ($\text{P-101} \rightarrow \text{E-101} \rightarrow \text{E-102} \dots \rightarrow \text{C-101}$). Highlight the disclaimer: *Representative Process Topology — Not a Proprietary Plant Blueprint*.
2. **E-102 State Inspection**: Click asset **E-102**. Show live derived $R_f$, $UA$, temperature differential, and M4.0 Ridge prognosis. Point out the Reliability Gate status (`PASS`) and decision (`CLEANING WINDOW — REVIEW`).
3. **The Trust Gate Stress Demonstration**: Press <kbd>3</kbd> or click **TRUST GATE VISUAL** $\rightarrow$ **+6σ REGIME SHIFT**. Show how the gate instantly switches to `ABSTAIN` (`REGIME_OOD`), withholding the AI recommendation and activating the fixed-policy fallback.
4. **Data Firewall & Intake**: Click **PLANT INTAKE**. Demonstrate dragging plant evidence (PDF, P&ID, XLSX) and highlight the firewall disclaimer: *Uploaded industrial files are not silently mixed into model training.*

---

## 3. 5-Minute Technical Deep Dive Sequence
1. **Scientific Evidence Trace**: Click **WHY? / EVIDENCE** to step through the 6-stage chain: Raw Measurements $\rightarrow$ M2 Physics $\rightarrow$ Derived $R_f$ $\rightarrow$ M4 Prognosis $\rightarrow$ M5 Reliability Gate $\rightarrow$ M6 Decision.
2. **Multilingual Architecture**: Toggle the language selector between **English**, **தமிழ் (Tamil)**, and **हिन्दी (Hindi)** to show localized explanations while asset IDs (`E-102`) and telemetry units remain strictly invariant.
3. **Bounded Process Chemistry**: Click **CHEMISTRY DEMO** to show crude fraction compositions and thermal deposition steps with explicit kinetics disclaimers (`STOICHIOMETRIC / EQUILIBRIUM MODE ONLY`).
4. **Model Provenance**: Click **PROVENANCE** to show dataset statistics (64,000 rows, 5 exchangers, 1h sampling) and SHA-256 checksum verification (`c8ed7d9c...4b4d9`).

---

## 4. Judging Defense Q&A

### Q1: "Is this real refinery data?"
> **Answer**: No. The current prognosis model is trained and benchmarked strictly on a synthetic physics-based dataset (64,000 rows, 5 exchangers). We explicitly label this across the interface. The process topology is representative, not a proprietary plant blueprint.

### Q2: "What is the core scientific contribution if fouling prediction isn't new?"
> **Answer**: We are not claiming fouling prognosis itself is novel. The defensible contribution is the domain-specific reject-option reliability-gated decision layer (M5) plus explicit fixed-policy fallback (M6). Predictions are prevented from influencing maintenance when evidence is insufficient.

### Q3: "What happens when your AI is wrong or out of distribution?"
> **Answer**: FOUL-X **abstains**. The forecast remains available for engineering inspection, but the maintenance recommendation is withheld, and the system cleanly retains the fixed plant maintenance policy.

### Q4: "Why not just rely on the model prediction?"
> **Answer**: Statistical forecast accuracy on clean data does not equal decision safety during plant transients or sensor failures. A model can produce a prediction even when operating outside its validated convex hull.

### Q5: "Is the +6σ regime shift realistic?"
> **Answer**: It is a controlled synthetic stress test designed to verify that the Reliability Gate correctly triggers `REGIME_OOD` and abstains under distributional shift. It is not presented as a real refinery safety guarantee.

### Q6: "Is this a full digital twin?"
> **Answer**: We describe it as an Industrial Digital Shadow. A true operational digital twin requires site-specific real-time DCS synchronization, bi-directional control, and validated physical calibration beyond a prototype scope.
