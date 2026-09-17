"""
Artifact Generation Script for FOUL-X M11.0 Red-Team Failure-Safety Validation.

Executes RedTeamHarness and generates:
- artifacts/m11/redteam_manifest.json
- artifacts/m11/scenario_results.json
- artifacts/m11/redteam_summary.json
"""

import json
from pathlib import Path

from src.foulx.redteam.harness import RedTeamHarness
from src.foulx.redteam.schemas import RedTeamManifest


def run_m11_artifact_pipeline():
    print("Initializing FOUL-X M11.0 Red-Team Failure-Safety Harness...")
    harness = RedTeamHarness()

    artifact_dir = Path("artifacts/m11")
    artifact_dir.mkdir(parents=True, exist_ok=True)

    print("Executing all 10 Red-Team failure-safety scenarios...")
    results, summary = harness.run_all_scenarios()

    # 1. scenario_results.json
    print("Writing scenario_results.json...")
    res_data = [r.model_dump() for r in results]
    with open(artifact_dir / "scenario_results.json", "w") as f:
        json.dump(res_data, f, indent=2)

    # 2. redteam_summary.json
    print("Writing redteam_summary.json...")
    with open(artifact_dir / "redteam_summary.json", "w") as f:
        json.dump(summary.model_dump(), f, indent=2)

    # 3. redteam_manifest.json
    print("Writing redteam_manifest.json...")
    manifest = RedTeamManifest(
        scenarios_evaluated=[r.scenario_code for r in results]
    )
    with open(artifact_dir / "redteam_manifest.json", "w") as f:
        json.dump(manifest.model_dump(), f, indent=2)

    print(f"M11 artifact generation complete! {summary.passed_scenarios}/{summary.total_scenarios} scenarios passed.")


if __name__ == "__main__":
    run_m11_artifact_pipeline()
