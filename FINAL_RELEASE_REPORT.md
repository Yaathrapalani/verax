# PLANT-X / FOUL-X — Final Release Report

### Release Tag & Commit
- **Release Version**: `v0.1.0-rc1`
- **Git Commit SHA**: `5d8abce` (`release: PLANT-X FOUL-X release candidate v0.1.0-rc1`)
- **Git Branch**: `main`
- **Repository Remote**: Ready for GitHub remote push (`git push -u origin main && git push origin v0.1.0-rc1`)

---

### Engineering & Scientific Verification Status

| Verification Step | Result | Target | Status |
| :--- | :--- | :--- | :--- |
| **Backend Python Unit Tests** | `116 / 116 PASS` | 100% Pass | **VERIFIED** |
| **Frontend Production Build** | `PASS (0 errors)` | Clean TypeScript Build | **VERIFIED** |
| **Raw Dataset SHA-256 Hash** | `c8ed7d9c...4b4d9` | Checksum Match | **VERIFIED** |
| **M2 Physics State Estimator** | Frozen & Validated | Energy Balance $|Q_t - Q_s|/Q_{max} \le 5\%$ | **VERIFIED** |
| **M4.0 Causal Ridge Prognosis** | Frozen & Validated | $+21.4\%$ to $+28.9\%$ MAE vs Persistence | **VERIFIED** |
| **M5.0 Reliability Gate** | Frozen & Validated | 4-Check Gate (Data, Sensor, Phys, OOD) | **VERIFIED** |
| **M6.0 Decision Engine** | Frozen & Validated | Fixed-Policy Fallback Mapping | **VERIFIED** |
| **M7.0 Policy Stress Test** | Frozen & Validated | $+6\sigma$ Shift ($200/200$ Abstained, 0 Harmful) | **VERIFIED** |
| **M9.0 Deterministic Replay** | Frozen & Validated | Temporal State Reconstruction ($t \in [44800, 63999]$) | **VERIFIED** |
| **M11.0 Red-Team Failure Harness** | Frozen & Validated | 10/10 Failure Stress Scenarios Passed | **VERIFIED** |
| **Security / Secret Audit** | 0 Secrets Found | Clean Repository Hygiene | **VERIFIED** |

---

### Public Demo & Vercel Configuration Handoff

The frontend is prepared for instant standalone static deployment on Vercel:

- **Root Directory**: `frontend`
- **Framework Preset**: `Vite`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`
- **SPA Rewrites**: Configured via [`frontend/vercel.json`](file:///Users/anush/Downloads/FOUL-X_DEV/frontend/vercel.json)

---

### Demo Scenarios & Judging Runbook
Detailed runbook instructions and defense Q&A created in [`docs/JUDGING_RUNBOOK.md`](file:///Users/anush/Downloads/FOUL-X_DEV/docs/JUDGING_RUNBOOK.md):
1. **Normal Operating Regime**: Reliability Gate `PASS` $\rightarrow$ Decision Support Active (`CLEANING WINDOW — REVIEW`).
2. **Shifted Regime (+6σ)**: Reliability Gate `ABSTAIN` (`REGIME_OOD`) $\rightarrow$ AI Action Withheld $\rightarrow$ Fixed Policy Active.
3. **Plant Data Firewall**: Uploaded evidence attached cleanly as context without contaminating training.
4. **Multilingual Architecture**: English / Tamil / Hindi language toggle.
5. **Bounded Chemistry**: Deposition mechanism visualization with explicit kinetics disclaimers.

---

### Scientific Boundaries & Disclaimers
1. **Advisory Decision Support**: Recommendations require human engineering approval. Zero autonomous plant/valve control.
2. **Benchmark Scope**: Model evaluation is strictly based on the 64,000-row synthetic benchmark dataset (`c8ed7d9c...4b4d9`).
3. **Representative Topology**: Crude preheat train topology is representative and not a proprietary plant blueprint.

---

### Judge-Ready Status
**READY** — All 116 unit tests, production build checks, dataset checksums, documentation, git tags, and deployment handoffs are complete.
