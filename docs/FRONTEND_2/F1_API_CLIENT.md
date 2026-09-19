# F1 Typed API Client Documentation

## Module Structure
- `frontend/src/api/types.ts`: TypeScript interfaces for `ApiState<T>`, `HealthCheckResponse`, `ReplayManifestResponse`, `PhysicsStateDTO`, `ReliabilityStateDTO`, `DecisionStateDTO`, and `ReplaySnapshotDTO`.
- `frontend/src/api/client.ts`: `PlantApiClient` implementing strongly typed fetch calls to `/health`, `/api/manifest`, `/api/exchangers`, and `/api/replay/snapshot`.

## State Pattern
All API calls return `ApiState<T>` with status (`LOADING` | `SUCCESS` | `ERROR` | `UNAVAILABLE`), data payload, error message, and ISO timestamp.
