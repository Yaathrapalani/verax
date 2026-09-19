# F1 Mock Data Migration Report

## Audit & Classification
1. `DEMO_DATA`: Offline fallback data retained strictly for controlled offline demo when API is unreachable.
2. `BACKEND_DATA`: Replaced with live fetch calls to `/api/replay/snapshot`.
3. `STATIC_REFERENCE_DATA`: Units catalog and physical constants ($C_p$).
4. `UNAVAILABLE_STATE`: Preserved for EOS, Transport, Pump Hydraulics, Valve Models.
