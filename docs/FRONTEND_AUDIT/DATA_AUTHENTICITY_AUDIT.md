# PLANT-X Data Authenticity Audit

| DISPLAYED VALUE | OBSERVED METRIC | CLASSIFICATION | SOURCE TRACEABILITY |
|---|---|---|---|
| E-102 Fouling Resistance ($R_f$) | `0.00042 m²K/W` | `SIMULATED` | `mockData.ts` (Derived from Stage 6 baseline dataset cycle) |
| Heat Transfer Rate ($Q$) | `4.12 MW` | `DERIVED` | Stage 12 Mass/Energy balance equation $Q = \dot{m} C_p \Delta T$ |
| Overall Heat Transfer Coefficient ($U$) | `420 W/m²K` | `DERIVED` | Stage 14 Heat Exchanger solver $1/U = 1/U_0 + R_f$ |
| Temperature Difference ($\Delta T_{LMTD}$) | `38.4 °C` | `DERIVED` | Stage 14 LMTD counter-current formula |
| Trust Gate Status | `PASS` / `ABSTAIN` | `DERIVED` | Stage 7 Trust Gate threshold evaluation |
| Stress Test Shift | `+6.0 σ` | `SIMULATED` | Interactive slider state in `TrustGateModal.tsx` |
| Hypotheses H1–H5 Confidence | `84% / 12% / 4%` | `DERIVED` | Stage 8 Investigation Intelligence hypothesis weighting |
| EOS Property Package | `IDEAL_GAS` | `ASSUMED` | Stage 13 Thermodynamic Engine bounds |
| Equation of State Status | `UNSUPPORTED` | `UNAVAILABLE` | Stage 13 Research Prototype boundary requirement |
| Transport Properties Status | `UNAVAILABLE` | `UNAVAILABLE` | Stage 13 physical scope limits |
| Pump Hydraulics Status | `PUMP_HYDRAULICS_UNAVAILABLE` | `UNAVAILABLE` | Stage 14 scope limitation |
| Valve Model Status | `VALVE_MODEL_UNAVAILABLE` | `UNAVAILABLE` | Stage 14 scope limitation |
| Financial Savings Projection | `$42,000 / clean` | `REPRESENTATIVE` | `mockData.ts` explicitly labeled as advisory recommendation |
| Dataset SHA-256 Checksum | `c8ed7d9c...4b4d9` | `OBSERVED` | Exactly matches backend frozen dataset SHA-256 |
