# Mock Data Policy

## Classification of Client Data
1. **DEMO_DATA**: Explicitly tagged client-side simulation state used for offline demonstration (`mockData.ts`).
2. **BACKEND_DATA**: Live responses fetched from REST API endpoints (`/api/plant/...`).
3. **STATIC_REFERENCE_DATA**: Fixed physical constants ($C_p$, units, physical formulas).
4. **UNAVAILABLE_STATE**: Explicitly declared missing capabilities (`EOS = UNSUPPORTED`, `Transport = UNAVAILABLE`, `PUMP_HYDRAULICS_UNAVAILABLE`).

## Policy Rules
- Client-side demo data must NEVER be presented as unverified live plant telemetry without appropriate truth state tags (`SIMULATED` / `REPRESENTATIVE`).
- When backend REST endpoints are active, `PlantClientState` seamlessly hydrates from API calls.
