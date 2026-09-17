# M10.0 Reproducible Deployment Specification

## 1. Container Architecture & Orchestration
The FOUL-X system is containerized into two services using Docker Compose:

```
                  ┌───────────────────────────────┐
                  │    foulx-frontend (Port 3000) │
                  │    Nginx (Alpine) Static UI   │
                  └───────────────┬───────────────┘
                                  │
                                  ▼ CORS / REST
                  ┌───────────────────────────────┐
                  │    foulx-api (Port 8000)      │
                  │    FastAPI + Uvicorn          │
                  │    Python 3.11-slim + uv      │
                  └───────────────┬───────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 ▼                                 ▼
      Raw Data (SHA-256 Verified)        Validated Artifacts (M2–M9)
```

## 2. Dependencies & Environment Reproducibility
- **Backend**: Python 3.11 slim environment with Astral `uv` package manager (`uv pip install --system -r requirements.txt`). Scientific dependencies pinned in `requirements.txt`.
- **Frontend**: Node 20 Alpine multi-stage Docker build utilizing `npm ci` for lockfile dependency reproducibility.

## 3. FastAPI Service & Health Endpoint
- App Entrypoint: `src/foulx/api/app.py`
- **Health Check (`GET /health`)**:
  ```json
  {
    "status": "healthy",
    "service": "foulx-api",
    "version": "1.0.0",
    "artifacts_loaded": true,
    "configuration_loaded": true,
    "core_ready": true,
    "plant_connectivity": "DISCONNECTED_PROTOTYPE_MODE",
    "representation": "INDUSTRIAL DIGITAL SHADOW — PROTOTYPE",
    "dataset_checksum": "c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9"
  }
  ```

## 4. Native vs Docker Canonical Reproducibility Comparison
- **Test Snapshots**: `E02 / t=45000 / NORMAL` & `E02 / t=45000 / SHIFTED`
- **Native vs API Output**: 100% byte-for-byte serialized equivalence verified via `tests/deployment/test_reproducibility.py`.
- **Dataset Hash Invariant**: SHA-256 checksum `c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9` is verified prior to and after execution.

## 5. Deployment Artifacts (`artifacts/m10/`)
- `deployment_manifest.json`
