# FOUL-X M1-A Dataset Discovery and Evidence Registry

**Date:** 2026-09-16  
**Purpose:** Identify defensible data sources for FOUL-X P01 before any model development.

## Decision status

**Primary development candidate:** Synthetic Shell-and-Tube Heat Exchanger Fouling dataset (Kaggle, Apache-2.0), subject to local download/schema verification.

**Secondary process-behaviour candidate:** Hybrid Thermodynamic and Machine Learning Optimization of Plate Heat Exchanger Performance underlying dataset (Zenodo DOI 10.5281/zenodo.17154403, CC BY 4.0). It contains high-resolution production-batch monitoring and long-term fouling-trend data, but the published description emphasizes indirect performance/fouling indicators rather than a directly observed R_f target. Use for process-behaviour/validation analysis, not automatically as a supervised R_f target.

**Stress-test candidate:** FCCU Dataset from Machine Learning for Process Systems Engineering. It contains simulated refinery process data with a dedicated heat-exchanger-fouling fault, plus sensor-drift and pressure-drop faults. It is useful for stress/OOD/fault scenarios, not as the primary fouling-regression target.

**Experimental benchmark candidates:**
- Jradi et al., Scientific Reports 2022: 361 experimental observations across 7 operating cycles in a phosphoric-acid concentration heat exchanger, with fouling resistance as output. The paper reports the variables and ranges, but this search did not establish an openly downloadable raw CSV. Treat as literature/benchmark evidence unless the raw data are obtained from the authors.
- Berce et al., Applied Thermal Engineering 2025: three experimental brazed-plate-heat-exchanger fouling case studies with 1 Hz measurements and RUL evaluation. The paper states data are available on request. Treat as a potential external validation source, not an immediately accessible dataset.

## Candidate 1 — Synthetic Shell-and-Tube Heat Exchanger Fouling

- **Source:** Kaggle, `webjdi/synthetic-shell-and-tube-heat-exchanger-fouling`
- **Classification:** Synthetic, physics-based simulation
- **License:** Apache 2.0 as stated on the dataset page
- **Scale:** 2,000 hourly timesteps; 88 columns; five shell-and-tube exchangers in a refinery crude preheat train
- **Temporal structure:** Yes, hourly sequence
- **Measured inputs:** noisy tube/shell flow, tube/shell inlet/outlet temperatures, heat-capacity variables, global crude properties
- **Target:** true fouling resistance R_f for each exchanger
- **Additional validation targets:** true U, true heat duty, true wall temperature
- **Cleaning events:** The dataset page describes fouling progression but the current public description does not establish explicit real cleaning-event labels. This must be verified from the downloaded CSV before using cycle-aware training.
- **Regime variables:** crude API, TAN, chlorides, flow, temperatures
- **Physics basis:** Kern-Seaton-style deposition/removal dynamics with causal links to crude properties, wall temperature and flow
- **Recommended use:** TRAIN / VALIDATION / STRESS TEST
- **Main limitation:** synthetic data are not plant measurements and cannot prove industrial generalization.
- **Critical rule:** true/hidden columns must never enter model features.

Source: urlKaggle dataset pagehttps://www.kaggle.com/datasets/webjdi/synthetic-shell-and-tube-heat-exchanger-fouling

## Candidate 2 — Brewery Plate Heat Exchanger Dataset

- **Source:** Zenodo, DOI 10.5281/zenodo.17154403, underlying data for a 2025 open study
- **Classification:** Experimental/industrial production data with derived thermodynamic quantities
- **License:** CC BY 4.0 according to the associated publication
- **Scale:** >50 production batches at 1 Hz plus 480 batches for long-term fouling-trend analysis
- **Temporal structure:** Yes
- **Variables described:** inlet/outlet temperatures, flow rates, pressure differential, thermophysical properties, heat duty, effectiveness, LMTD, U, NTU and derived fouling-rate slope
- **Direct R_f target:** Not established from the available publication description. Fouling trend is inferred through performance/effectiveness and slope metrics.
- **Cleaning events:** Not established from the publication description used in this audit
- **Recommended use:** VALIDATION / PROCESS-BEHAVIOUR CHECK / BACKUP
- **Main limitation:** different application domain and target formulation from FOUL-X's shell-and-tube R_f forecasting task; do not force it into the same supervised target without a justified mapping.

Source: urlZenodo dataset recordhttps://doi.org/10.5281/zenodo.17154403

## Candidate 3 — FCCU Process Dataset

- **Source:** Machine Learning for Process Systems Engineering, FCCU Dataset
- **Classification:** Synthetic process simulation
- **Scale:** seven CSV simulations, 46 measured signals plus time
- **Sampling:** one-minute outputs
- **Fouling scenario:** preheater heat-transfer coefficient UAf decreases beginning at 120 min, with staged degradation
- **Other relevant stress scenarios:** flow-sensor drift and increased pressure drop
- **Cleaning events:** No explicit cleaning-cycle labels established
- **R_f target:** No direct R_f target
- **Recommended use:** STRESS TEST / SENSOR-FAILURE DEMO / OOD SCENARIO SOURCE
- **Main limitation:** fouling is represented as a process fault rather than a direct fouling-resistance trajectory.

Source: urlFCCU Dataset pagehttps://mlforpse.com/fccu-dataset/

## Candidate 4 — Phosphoric Acid Heat Exchanger Experimental Study

- **Citation:** Jradi, Marvillet & Jeday, Scientific Reports, 2022, DOI 10.1038/s41598-022-24689-2
- **Classification:** Experimental industrial process data
- **Scale:** 361 observations across 7 operating cycles over a one-year collection period
- **Variables:** time, acid inlet temperature, acid outlet temperature, steam temperature, acid density, acid volume flow
- **Target:** fouling resistance
- **Operating horizon reported:** 0–122 h
- **Important limitation:** the paper's modeling split was random 70/15/15. FOUL-X must not reuse that split for temporal evaluation. If raw data are acquired, we will reconstruct chronological cycle-aware splits.
- **Raw data availability:** Not established as an openly downloadable dataset in this M1-A search.
- **Recommended use:** EXTERNAL BENCHMARK / POTENTIAL VALIDATION if authors provide data

Source: urlScientific Reports articlehttps://doi.org/10.1038/s41598-022-24689-2

## Candidate 5 — Fouled Plate Heat Exchanger RUL Experimental Cases

- **Citation:** Berce et al., Applied Thermal Engineering, 2025, DOI 10.1016/j.applthermaleng.2025.126954
- **Classification:** Experimental laboratory fouling data
- **Scale:** three brazed plate heat exchanger fouling case studies
- **Sampling:** 1 Hz during experiments
- **Signals:** hot/cold inlet temperatures and flow rates, with performance-derived fouling/degradation quantities
- **RUL relevance:** direct demonstration of real-time RUL estimation under dynamic flow disturbances
- **Data access:** paper states data will be made available on request
- **Recommended use:** LITERATURE BENCHMARK / FUTURE EXTERNAL VALIDATION
- **Main limitation:** no immediate open raw-data access established

Source: urlScienceDirect articlehttps://doi.org/10.1016/j.applthermaleng.2025.126954

## Candidate 6 — NTNU/Equinor Heat Exchanger Condition-Monitoring Thesis Repository

- **Source:** public GitHub repository `hermanwh/master-thesis`
- **Classification:** mixed simulated and real facility data in the original research, but the public repository does not expose all underlying facility datasets
- **Relevant content:** modular heat-exchanger condition monitoring code, profiling notebooks, LSTM/MLP/linear models and uncertainty experiments
- **Key methodological warning:** the thesis notes that fouling is difficult to measure directly in real facilities and that simulated data provide controlled ground truth
- **Recommended use:** RESEARCH/METHODOLOGY REFERENCE, not primary training data unless data provenance is independently verified

Source: urlPublic repositoryhttps://github.com/hermanwh/master-thesis

## M1-A conclusion

The strongest immediately usable dataset identified for the FOUL-X core supervised task is the Kaggle synthetic shell-and-tube dataset because it combines temporal structure, noisy plant-like measurements, multiple exchangers, operating-condition variables and an explicit R_f target under an open Apache-2.0 license.

However, it is **not sufficient to claim industrial validation**. The project therefore keeps three evidence layers separate:

1. **Core model development:** open physics-based synthetic dataset.
2. **Process-behaviour validation:** independent experimental/industrial-style datasets where target semantics are compatible.
3. **Reliability stress testing:** controlled sensor faults, regime shifts and synthetic perturbations.

No raw proprietary plant data are required for the hackathon. Any future plant dataset must be anonymized and permissioned.

## Immediate next action

Download and profile the primary dataset locally. Verify the actual CSV schema before freezing M1-B. In particular, confirm:

- exact column names
- missingness
- duplicate timestamps
- monotonic time
- exchanger identifiers
- whether cleaning events are explicit or must be inferred
- target distributions
- target continuity/reset behaviour
- availability of pressure/ΔP variables
- availability of variables needed for the planned thermal/hydraulic state estimator
- whether the hidden ground-truth columns can be cleanly separated from measured inputs
