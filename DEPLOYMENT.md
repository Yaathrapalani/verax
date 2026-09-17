# PLANT-X / FOUL-X Deployment Guide

This document provides complete instructions for local development, Docker deployment, and public frontend (Vercel) hosting.

---

## 1. Local Development Setup

### Backend Environment (Python + uv)
1. **Prerequisites**: Python 3.11+, `uv` package manager (or `pip`).
2. **Install Dependencies**:
   ```bash
   uv sync
   ```
3. **Execute Backend Verification Tests**:
   ```bash
   PYTHONPATH=. uv run pytest -q
   ```
   *Expected Result*: `116 passed`.

4. **Generate M11 Red-Team Artifacts (Optional)**:
   ```bash
   PYTHONPATH=. uv run python scripts/generate_m11_artifacts.py
   ```

### Frontend Environment (Vite + React)
1. **Prerequisites**: Node.js 18+.
2. **Install & Build**:
   ```bash
   cd frontend
   npm ci
   npm run build
   ```
3. **Launch Local Frontend Dev Server**:
   ```bash
   npm run dev
   ```
   *Access UI at*: `http://localhost:3000`

---

## 2. Docker & Docker Compose Deployment

### Launching with Docker Compose
```bash
# 1. Validate Docker Compose configuration
docker compose config

# 2. Build containers
docker compose build

# 3. Start containers in daemon mode
docker compose up -d

# 4. Verify container status
docker compose ps
```

### Access Endpoints
- **Frontend Command Center UI**: `http://localhost:3000`
- **FastAPI Backend Service**: `http://localhost:8000`
- **API Health Check**: `curl http://localhost:8000/health`

### Expected Health Response
```json
{
  "status": "healthy",
  "service": "foulx-api",
  "version": "1.0.0",
  "artifacts_loaded": true,
  "configuration_loaded": true,
  "core_ready": true,
  "plant_connectivity": "DISCONNECTED_PROTOTYPE_MODE"
}
```

### Shutdown
```bash
docker compose down
```

---

## 3. Vercel Public Frontend Deployment

The public frontend demo is designed to run statically/independently on Vercel with zero external paid API dependencies.

### Vercel Project Import Settings
- **Repository**: Select imported GitHub Repository
- **Root Directory**: `frontend`
- **Framework Preset**: `Vite`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

### Deployment Steps (Vercel Dashboard)
1. Navigate to [Vercel Dashboard](https://vercel.com/new).
2. Import the GitHub repository `PLANT-X_FOUL-X`.
3. Set **Root Directory** to `frontend`.
4. Leave Framework Preset as `Vite`.
5. Click **Deploy**.

---

## 4. Release Verification Checklist

Run these commands prior to declaring a release:
```bash
# 1. Check Python backend test suite
PYTHONPATH=. uv run pytest -q

# 2. Check frontend TypeScript build
cd frontend && npm run build && cd ..

# 3. Check dataset SHA-256 integrity
python3 -c "import hashlib; print(hashlib.sha256(open('data/raw/heat_exchanger_fouling_dataset.csv', 'rb').read()).hexdigest())"
```

Expected SHA-256 Output: `c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9`
