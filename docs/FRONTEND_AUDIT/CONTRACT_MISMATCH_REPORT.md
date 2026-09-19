# Frontend / Backend Contract Mismatch Report

## Overview
This report documents mismatches between the current frontend UI implementation and the backend Python service layer.

## Mismatch Audit Findings
1. **HTTP API Connectivity**:
   - **Frontend Expects**: Standalone React state handlers using compiled client-side `mockData.ts`.
   - **Backend Provides**: FastAPI endpoints `/api/plant/...`, `/api/foulx/...`.
   - **Severity**: `MEDIUM` (Does not break UI live demo, but frontend runs on `UI_ONLY`/`PARTIAL` client mock state).
2. **Data Structure Parity**:
   - Field names in `mockData.ts` match domain schema in `src/plantx/schema/` (e.g. `fouling_resistance`, `confidence`, `gate_status`).
   - No broken field mappings or type mismatches discovered.
3. **Contract Truth Enforcement**:
   - Both backend and frontend agree on unavailable capabilities (`EOS = UNSUPPORTED`, `Transport = UNAVAILABLE`, `PUMP_HYDRAULICS_UNAVAILABLE`).
   - No contract violations present in UI claims.
