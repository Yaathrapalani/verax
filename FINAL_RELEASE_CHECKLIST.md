# FINAL RELEASE CHECKLIST: PLANT-X / FOUL-X v0.1.0-rc1

## REPOSITORY & CODE HYGIENE
- [x] Repository clean and structured
- [x] Root README.md rebuilt with full architecture & disclaimers
- [x] DEPLOYMENT.md updated with local, Docker, and Vercel instructions
- [x] docs/JUDGING_RUNBOOK.md created with elevator pitch & defense Q&A
- [x] Zero secrets, private keys, or API tokens committed
- [x] .gitignore excludes node_modules, build outputs, and local env files

## ENGINEERING VERIFICATION
- [x] 116 / 116 Backend Python unit tests passing (`uv run pytest -q`)
- [x] Frontend TypeScript production build passing (`cd frontend && npm run build`)
- [x] Dataset SHA-256 checksum verified (`c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9`)
- [x] M2–M11 validated engineering logic frozen and unmodified

## DOCKER DEPLOYMENT
- [x] Docker Compose configuration valid (`docker compose config`)
- [x] Docker containers build cleanly (`docker compose build`)
- [x] Docker stack launches in daemon mode (`docker compose up -d`)
- [x] FastAPI backend health endpoint returns healthy (`curl http://localhost:8000/health`)
- [x] Frontend reachable at `http://localhost:3000`

## VERCEL & PUBLIC FRONTEND READINESS
- [x] Vite frontend configured for standalone static demo mode
- [x] `frontend/vercel.json` SPA rewrite configuration created
- [x] Vercel build settings documented (`Root: frontend`, `Build: npm run build`, `Output: dist`)

## DEMO SCENARIOS & SAFETY INVARIANTS
- [x] Normal Regime: Gate `PASS` $\rightarrow$ `CLEANING WINDOW — REVIEW`
- [x] Shifted Regime (+6σ): Gate `ABSTAIN` (`REGIME_OOD`) $\rightarrow$ `AI ACTION WITHHELD`
- [x] Fixed Policy Fallback: Active under abstention
- [x] Evidence Trace: 6-stage provenance graph functional
- [x] Industrial Intake & Data Firewall: Clear boundary between evidence and training data
- [x] Multilingual Support: English, Tamil, and Hindi toggling
- [x] Bounded Chemistry: Deposition mechanism visualization with kinetics disclaimers
- [x] Replay Engine: Historical state reconstruction functional
