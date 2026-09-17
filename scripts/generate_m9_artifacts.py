"""
Artifact Generation Script for FOUL-X M9.0 Replay Engine.

Generates canonical ReplaySnapshots (t=44800, t=45000, t=54400, shifted t=45000)
and ReplayManifest in artifacts/m9/.
"""

import os
import json
from pathlib import Path

from src.foulx.replay.schemas import ReplayMode
from src.foulx.replay.service import ReplayService


def run_m9_artifact_pipeline():
    print("Initializing FOUL-X Replay Service for M9 artifact generation...")
    service = ReplayService()

    artifact_dir = Path("artifacts/m9")
    artifact_dir.mkdir(parents=True, exist_ok=True)

    # 1. snapshot_t44800.json
    print("Generating snapshot_t44800.json...")
    snap_44800 = service.get_snapshot(44800.0, "E01", ReplayMode.NORMAL)
    with open(artifact_dir / "snapshot_t44800.json", "w") as f:
        json.dump(snap_44800.to_dict(), f, indent=2)

    # 2. snapshot_t45000.json
    print("Generating snapshot_t45000.json...")
    snap_45000 = service.get_snapshot(45000.0, "E01", ReplayMode.NORMAL)
    with open(artifact_dir / "snapshot_t45000.json", "w") as f:
        json.dump(snap_45000.to_dict(), f, indent=2)

    # 3. snapshot_t54400.json
    print("Generating snapshot_t54400.json...")
    snap_54400 = service.get_snapshot(54400.0, "E01", ReplayMode.NORMAL)
    with open(artifact_dir / "snapshot_t54400.json", "w") as f:
        json.dump(snap_54400.to_dict(), f, indent=2)

    # 4. shifted_snapshot_t45000.json
    print("Generating shifted_snapshot_t45000.json...")
    snap_shifted_45000 = service.get_snapshot(45000.0, "E01", ReplayMode.SHIFTED)
    with open(artifact_dir / "shifted_snapshot_t45000.json", "w") as f:
        json.dump(snap_shifted_45000.to_dict(), f, indent=2)

    # 5. replay_manifest.json
    print("Generating replay_manifest.json...")
    manifest = service.get_manifest()
    with open(artifact_dir / "replay_manifest.json", "w") as f:
        json.dump(manifest.to_dict(), f, indent=2)

    print("M9 artifact generation complete!")


if __name__ == "__main__":
    run_m9_artifact_pipeline()
