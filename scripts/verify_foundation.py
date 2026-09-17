from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
required = [
    "README.md",
    "AGENTS.md",
    "docs/PRD.md",
    "docs/TRD.md",
    "docs/architecture.md",
    "docs/assumptions.md",
    "docs/research_claims.md",
    "docs/validation_plan.md",
    "src/foulx/__init__.py",
    "tests/test_foundation.py",
]
missing = [p for p in required if not (ROOT / p).exists()]
if missing:
    raise SystemExit("Missing required files:\n" + "\n".join(missing))
print(f"FOUL-X foundation OK: {len(required)} required files present")
