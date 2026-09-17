# PLANT-X / FOUL-X

**Industrial Process Intelligence & Trust-Gated Heat Exchanger Fouling Prognosis**

> *"FOUL-X does not treat every prediction as actionable."* — It separates prognosis from decision by evaluating whether the current evidence supports the prediction.

---

## 1. Executive Summary

**PLANT-X** is an industrial process-intelligence architecture that converts heterogeneous plant evidence into an auditable process representation. 

**FOUL-X** is the first validated vertical implementation on PLANT-X, specifically addressing heat-exchanger fouling prognosis and reliability-aware maintenance support. Rather than relying blindly on AI predictions, FOUL-X introduces a domain-specific **Reliability Gate (M5)** and a **Decision Engine (M6)** that either approve decision support or **ABSTAIN**, cleanly falling back to fixed plant maintenance policies when operating conditions shift outside validated bounds.

---

## 2. The Core Problem & Thesis

In heavy process industries (e.g., oil refining crude preheat trains), heat exchanger fouling degrades thermal efficiency, increases fuel consumption, and raises emissions. Traditional maintenance relies on fixed-interval cleaning schedules, while naive AI models can issue false or unsupported recommendations during process transients.

**The FOUL-X Thesis**:
$$\text{PLANT EVIDENCE} \longrightarrow \text{PHYSICS STATE} \longrightarrow \text{PROGNOSIS} \longrightarrow \text{RELIABILITY GATE} \longrightarrow \begin{cases} \text{PASS} & \implies \text{DECISION SUPPORT} \\ \text{ABSTAIN} & \implies \text{FIXED POLICY FALLBACK} \end{cases}$$

---

## 3. Architecture & Engineering Pipeline

```
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│   RAW MEASUREMENTS      │ ──> │ M2 PHYSICS ESTIMATOR    │ ──> │ DERIVED FOULING (Rf)    │
│   (Temps, Flows, Press) │     │ (LMTD, Heat Duty, UA)   │     │  Rf = (1/UA) - (1/UA0)  │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
                                                                             │
                                                                             ▼
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│ M6 DECISION ENGINE      │ <── │ M5 RELIABILITY GATE     │ <── │ M4.0 CAUSAL RIDGE       │
│ (Operate / Review /     │     │ (4 Reliability Checks:  │     │ (Temporal Prognosis     │
│  Abstain + Fallback)    │     │  Data,Sensor,Phys,OOD)  │     │  1h, 6h, 24h horizons)  │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```

- **M2 Physics State**: Deterministic heat duty counter-current balance ($|Q_t - Q_s|/Q_{max} \le 5.0\%$) and overall heat transfer coefficient ($UA$).
- **M3 Baselines**: Persistence and Linear Trend forecasting over 1h, 6h, 24h, 72h, 168h.
- **M4.0 Causal Ridge**: Causal feature extraction (rolling windows $W \in \{6, 24, 72, 168\}$) fit strictly on training set ($t \le 44,799$).
- **M5.0 Reliability Gate**: Evaluates Data Completeness, Sensor Validity, Physics Consistency, and Historical Regime Support.
- **M6.0 Decision Engine**: Maps state to `OPERATE`, `CLEANING_REVIEW`, or `ABSTAIN` (forcing fixed plant policy fallback).
- **M7.0 Policy Experiment**: Evaluates Gated vs Un-gated decisions under controlled $+6\sigma$ operational regime shifts.
- **M9.0 Deterministic Replay**: Historical state reconstruction engine for times $t \in [44800, 63999]$.
- **M11.0 Red-Team Failure-Safety**: 10-scenario failure stress harness confirming 100% safety invariants held.

---

## 4. Reliability Gate & Stress-Test Demonstration

The **M5 Reliability Gate** evaluates 4 independent criteria before allowing an AI forecast to influence decision support:
1. **Data Completeness**: No missing critical sensor streams (`DATA_INVALID`).
2. **Sensor Validity**: Measurements within physical bounds ($0 \le T \le 450^\circ\text{C}$, `DATA_OUT_OF_RANGE`).
3. **Physics Consistency**: Thermodynamic energy balance satisfied (`PHYSICS_VIOLATION`).
4. **Regime Support**: Current operating point within historical convex hull and error variance bounds (`REGIME_OOD`).

### Controlled $+6\sigma$ Synthetic Stress Test
In controlled stress evaluation (M7 / M11):
- **Normal Operating Regime**: Gate status `PASS` $\rightarrow$ AI-assisted decision support active (`CLEANING WINDOW — REVIEW`).
- **Shifted Regime (+6σ)**: Gate status `ABSTAIN` (`REGIME_OOD`) $\rightarrow$ AI action withheld $\rightarrow$ Fixed-policy fallback active ($200/200$ cases abstained, $0$ harmful recommendations).

> *Note: This is a controlled synthetic stress test designed to verify gate logic, not a real-world field safety guarantee.*

---

## 5. Scientific Validation & Training Data Firewall

### Benchmark Provenance
- **Dataset**: `data/raw/heat_exchanger_fouling_dataset.csv` (Synthetic physics-based heat-exchanger fouling benchmark).
- **Rows / Exchangers**: 64,000 hourly rows across 5 shell-and-tube exchangers (E01–E05).
- **Cryptographic SHA-256 Checksum**: `c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9`
- **Chronological Split**: Train ($t=0\dots44,799$), Validation ($t=44,800\dots54,399$), Test ($t=54,400\dots63,999$).
- **Benchmark Result**: On this synthetic benchmark, M4.0 Causal Ridge achieved approximately **21–29% lower validation MAE** than Persistence across E01–E05 for 1h, 6h, and 24h horizons.

### Training Data Firewall
```
┌─────────────────────────────────────────────────────────────┐
│ INDUSTRIAL INTAKE (CSV, XLSX, PDF, P&ID, Datasheets, Logs)   │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Ingested strictly as CONTEXT)
                               ▼
 ┌───────────────────────────────────────────────────────────┐
 │               TRAINING DATA FIREWALL (BLOCKED)            │
 └─────────────────────────────┬─────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ CURRENT MODEL BENCHMARK (1 Validated Dataset Only)          │
│ data/raw/heat_exchanger_fouling_dataset.csv (SHA-256 Check)│
└─────────────────────────────────────────────────────────────┘
```
*Uploaded industrial plant files are ingested purely as context/mapping evidence and are **NOT** silently mixed into model training.*

---

## 6. Industrial Intake & Multi-Level Blueprint

PLANT-X supports intake across multiple file categories:
- **Data Formats**: CSV, XLSX, JSON, Parquet.
- **Engineering Documents**: PDF, PFD, P&ID, Equipment Datasheets, Maintenance Logs, Process Reports.
- **Visual Sources**: PNG, JPG, scanned engineering drawings.

**Intake Pipeline**:
$$\text{FILE} \longrightarrow \text{INSPECT} \longrightarrow \text{IDENTIFY} \longrightarrow \text{VALIDATE} \longrightarrow \text{MAP} \longrightarrow \text{CANONICAL PLANT MODEL}$$

If engineering identity cannot be established, the system explicitly flags: `UNRESOLVED — ENGINEERING MAPPING REQUIRED`.

### Representative Process Topology
The demonstration visualization reflects a representative Crude Distillation Unit (CDU) preheat train:
$$\text{CRUDE FEED} \rightarrow \text{P-101} \rightarrow \text{E-101} \rightarrow \text{E-102 (ATTN)} \rightarrow \text{E-103} \rightarrow \text{DESALTER} \rightarrow \text{E-104} \rightarrow \text{E-105} \rightarrow \text{PRE-FLASH} \rightarrow \text{F-101} \rightarrow \text{C-101}$$

> *Persistent Label: REPRESENTATIVE PROCESS TOPOLOGY — NOT A PROPRIETARY PLANT BLUEPRINT.*

---

## 7. Multilingual & Bounded Process Chemistry

### Multilingual Support
- Built-in language switcher supporting **English**, **தமிழ் (Tamil)**, and **हिन्दी (Hindi)**.
- Technical asset IDs (`E-102`), units ($^\circ\text{C}$, $\text{m}^2\cdot\text{K/W}$), and numerical values remain strictly invariant across languages.

### Bounded Process Chemistry
- Displays crude oil fractions (Naphtha, Kerosene, Gas Oil, Asphaltenes) and thermal coking deposition mechanisms.
- Explicitly flags property models (`Peng-Robinson EOS`) and kinetics limitations (`KINETICS UNAVAILABLE — EQUILIBRIUM / STOICHIOMETRIC MODE ONLY`).

---

## 8. Technology Stack & Verification Status

### Tech Stack
- **Frontend**: React 18, Vite 8, TypeScript, Tailwind CSS, Three.js / React Three Fiber, Lucide Icons.
- **Backend Core**: Python 3.11, FastAPI, NumPy, Pandas, scikit-learn, Pydantic v2.
- **Infrastructure & Testing**: Docker, Docker Compose, pytest, uv.

### Validation Status Table
| Component | Status | Details |
| :--- | :--- | :--- |
| **Backend Unit Tests** | **116 / 116 PASS** | Full coverage of M2–M11 modules (`uv run pytest -q`) |
| **Frontend Production Build** | **PASSED** | Clean build (`cd frontend && npm run build`) |
| **Raw Dataset SHA-256** | **PASSED** | Verified hash: `c8ed7d9c...4b4d9` |
| **M2 Physics State** | **PASSED** | Validated counter-current energy balance |
| **M5 Reliability Gate** | **PASSED** | 4-check verification & abstention layer |
| **M6 Decision Engine** | **PASSED** | Deterministic fixed-policy fallback mapping |
| **M11 Red-Team Harness** | **PASSED** | 10/10 failure stress scenarios passed |

---

## 9. Local Development & Deployment

### Quickstart (Local Python + Frontend)

1. **Clone & Setup Environment**:
   ```bash
   git clone <repo-url>
   cd FOUL-X_DEV
   uv sync
   ```

2. **Run Backend Tests**:
   ```bash
   PYTHONPATH=. uv run pytest -q
   ```

3. **Run Frontend Local Server**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open `http://localhost:3000` in browser.

### Docker Deployment

To build and launch the complete stack via Docker Compose:
```bash
docker compose config
docker compose build
docker compose up -d
docker compose ps
```
- API Health Check: `curl http://localhost:8000/health`
- Frontend UI: `http://localhost:3000`

---

## 10. Safety Boundary & Limitations

- **Advisory Decision Support**: FOUL-X recommendations remain strictly advisory. Human engineering approval is mandatory.
- **No Autonomous Control**: Zero direct connection to DCS/PLC control valves, automatic plant trips, or shutdown signals.
- **Synthetic Benchmark**: The model performance metrics reflect a synthetic physics-based benchmark dataset and must not be presented as measured monetary savings in an operating refinery.

---

## 11. Final Demo Sequence

For judging demonstrations:
1. **Open PLANT-X**: View Crude Preheat Train process flow header.
2. **Select E-102**: Inspect live telemetry,derived $R_f$, $UA$, and M4.0 prognosis.
3. **Check Reliability Gate**: View Data, Sensor, Physics, and Regime Support checks (`PASS`).
4. **Trigger Stress Shift (<kbd>3</kbd> or Trust Gate Button)**: Demonstrate Regime Support failure (`REGIME_OOD`), Reliability Gate `ABSTAIN`, and fallback to Fixed Policy.
5. **Open Evidence Trace**: View scientific provenance from historian measurements to decision support.
6. **Open Plant Intake / Data Firewall**: Demonstrate evidence ingestion with model training boundary.
7. **Switch Language**: Demonstrate English / Tamil / Hindi language toggle.
