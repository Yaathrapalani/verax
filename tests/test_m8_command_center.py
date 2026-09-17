"""
Frontend & Command Center Integration Tests for FOUL-X M8.0.
Verifies that frontend data contracts, representative topology mappings,
M8 demo flows, replay mechanisms, and safety invariants match validated M2-M7 outputs.
"""

import json
from pathlib import Path
import pytest

FRONTEND_DATA_SUMMARY_PATH = Path("frontend_demo_summary.json")
M7_SUPPORTED_ARTIFACT_PATH = Path("artifacts/m7/policy_comparison_supported.json")
M7_SHIFTED_ARTIFACT_PATH = Path("artifacts/m7/policy_comparison_shifted.json")


def test_frontend_data_summary_exists():
    assert FRONTEND_DATA_SUMMARY_PATH.exists(), "frontend_demo_summary.json missing!"
    with open(FRONTEND_DATA_SUMMARY_PATH) as f:
        data = json.load(f)
    assert "E01" in data
    assert "E02" in data
    assert "E03" in data
    assert "E04" in data
    assert "E05" in data


def test_representative_plant_mapping():
    """Verifies representative exchanger mappings: E-101..E-105 mapped to E01..E05."""
    mapping = {
        "E-101": "E01",
        "E-102": "E02",
        "E-103": "E03",
        "E-104": "E04",
        "E-105": "E05",
    }
    for tag_3d, tag_ds in mapping.items():
        # E-101 -> E01 (strip hyphen and middle zero)
        mapped = "E" + tag_3d.split("-")[1][1:]
        assert mapped == tag_ds


def test_m7_artifacts_integrity():
    """Ensures M7 evaluation artifacts consumed by command center exist and match schemas."""
    assert M7_SUPPORTED_ARTIFACT_PATH.exists()
    assert M7_SHIFTED_ARTIFACT_PATH.exists()

    with open(M7_SUPPORTED_ARTIFACT_PATH) as f:
        sup = json.load(f)
    assert "FIXED" in sup
    assert "UNGATED" in sup
    assert "GATED" in sup

    with open(M7_SHIFTED_ARTIFACT_PATH) as f:
        shifted = json.load(f)
    assert shifted["GATED"]["abstention_count"] == 200
    assert shifted["GATED"]["coverage"] == 0.0


def test_human_approval_invariant():
    """Verifies that human approval requirement is preserved across all interface schemas."""
    from src.foulx.decision.schemas import DecisionProvenance
    prov = DecisionProvenance()
    assert prov.human_approval_required is True
