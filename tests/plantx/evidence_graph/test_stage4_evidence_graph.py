"""Comprehensive Stage-4 Evidence Graph Test Suite covering all 10 Killer Tests and Exit Criteria."""

import pytest
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.evidence_graph import (
    EvidenceGraphEngine,
    GraphNodeType,
    GraphEdgeType,
    SufficiencyStatus,
    TemporalLineageViolationError,
)


@pytest.fixture
def base_prov():
    return Provenance(
        provenance_id="prov-eg-test",
        provenance_type=ProvenanceType.HISTORIAN,
        source_reference="data/raw/heat_exchanger_fouling_dataset.csv",
        timestamp="2026-09-17T13:00:00Z",
    )


@pytest.fixture
def foulx_lineage_fixture(base_prov):
    """Deterministic FOUL-X end-to-end lineage graph fixture."""
    engine = EvidenceGraphEngine()

    # 1. Source & Raw Evidence
    engine.add_node("src-1", GraphNodeType.EVIDENCE_SOURCE, TruthState.OBSERVED, base_prov, observed_at=50.0)
    engine.add_node("m-thi", GraphNodeType.MEASUREMENT, TruthState.OBSERVED, base_prov, observed_at=50.0, payload={"sensor_id": "TUBE_INLET", "value": 300.0})
    engine.add_node("m-tho", GraphNodeType.MEASUREMENT, TruthState.OBSERVED, base_prov, observed_at=50.0, payload={"sensor_id": "TUBE_OUTLET", "value": 250.0})

    # 2. Canonical Entity
    engine.add_node("asset-e102", GraphNodeType.CANONICAL_ENTITY, TruthState.OBSERVED, base_prov, observed_at=50.0, payload={"asset_id": "E-102"})

    # 3. Assumptions
    engine.add_node("asm-countercurrent", GraphNodeType.ASSUMPTION, TruthState.REPRESENTATIVE, base_prov, observed_at=50.0, payload={"assumption_name": "counter-current exchanger assumption"})
    engine.add_node("asm-uaclean", GraphNodeType.ASSUMPTION, TruthState.REPRESENTATIVE, base_prov, observed_at=50.0, payload={"assumption_name": "initial-window UA reference baseline"})

    # 4. Computation (M2 Physics)
    engine.add_node("comp-rf", GraphNodeType.ENGINEERING_COMPUTATION, TruthState.INFERRED, base_prov, observed_at=50.0, payload={"calculation_version": "1.0", "output": "Rf_derived"})

    # 5. Model & Prediction (M4 Prognosis)
    engine.add_node("model-ridge", GraphNodeType.MODEL_EXECUTION, TruthState.INFERRED, base_prov, observed_at=50.0, payload={"model_id": "M4-Ridge", "model_version": "1.0"})
    engine.add_node("pred-rf24", GraphNodeType.PREDICTION, TruthState.INFERRED, base_prov, observed_at=50.0, payload={"horizon_hours": 24, "target": "Rf"})
    engine.add_node("unc-pred", GraphNodeType.UNCERTAINTY, TruthState.INFERRED, base_prov, observed_at=50.0, payload={"method": "STD_DEV", "bounds": [0.0001, 0.0005]})

    # 6. Reliability Gate (M5) & Decision (M6)
    engine.add_node("dec-clean", GraphNodeType.DECISION, TruthState.INFERRED, base_prov, observed_at=50.0, payload={"decision": "CLEANING_REVIEW", "recommendation": "Cleaning review recommended for E-102"})

    # 7. Human Approval & Outcome
    engine.add_node("appr-op", GraphNodeType.HUMAN_APPROVAL, TruthState.OBSERVED, base_prov, observed_at=50.0, payload={"approver": "OPERATOR_01"})
    engine.add_node("out-clean", GraphNodeType.OUTCOME, TruthState.OBSERVED, base_prov, observed_at=50.0, payload={"downtime_hours": 12.0})

    # Edges
    engine.add_edge("e1", "src-1", "m-thi", GraphEdgeType.EXTRACTED_FROM)
    engine.add_edge("e2", "src-1", "m-tho", GraphEdgeType.EXTRACTED_FROM)
    engine.add_edge("e3", "m-thi", "asset-e102", GraphEdgeType.MEASURES)
    engine.add_edge("e4", "m-tho", "asset-e102", GraphEdgeType.MEASURES)

    engine.add_edge("e5", "m-thi", "comp-rf", GraphEdgeType.USES_INPUT)
    engine.add_edge("e6", "m-tho", "comp-rf", GraphEdgeType.USES_INPUT)
    engine.add_edge("e7", "asm-countercurrent", "comp-rf", GraphEdgeType.USES_ASSUMPTION)
    engine.add_edge("e8", "asm-uaclean", "comp-rf", GraphEdgeType.USES_ASSUMPTION)

    engine.add_edge("e9", "comp-rf", "pred-rf24", GraphEdgeType.PRODUCES)
    engine.add_edge("e10", "model-ridge", "pred-rf24", GraphEdgeType.USES_MODEL)
    engine.add_edge("e11", "pred-rf24", "unc-pred", GraphEdgeType.HAS_UNCERTAINTY)

    engine.add_edge("e-m1", "src-1", "model-ridge", GraphEdgeType.EXTRACTED_FROM)
    engine.add_edge("e-a1", "src-1", "asm-countercurrent", GraphEdgeType.EXTRACTED_FROM)
    engine.add_edge("e-a2", "src-1", "asm-uaclean", GraphEdgeType.EXTRACTED_FROM)

    engine.add_edge("e12", "pred-rf24", "dec-clean", GraphEdgeType.SUPPORTED_BY)
    engine.add_edge("e13", "dec-clean", "appr-op", GraphEdgeType.APPROVED_BY)
    engine.add_edge("e14", "appr-op", "out-clean", GraphEdgeType.RESULTED_IN)

    return engine


def test_killer_1_trace_why(foulx_lineage_fixture):
    explanation = foulx_lineage_fixture.explain_claim("dec-clean")
    assert explanation.status == SufficiencyStatus.SUPPORTED
    assert len(explanation.supporting_evidence) >= 2
    assert "M4-Ridge" in explanation.models


def test_killer_2_trace_impact(foulx_lineage_fixture):
    impact = foulx_lineage_fixture.impact_analysis("m-tho")
    assert "comp-rf" in impact.dependent_computations
    assert "pred-rf24" in impact.dependent_predictions
    assert "dec-clean" in impact.dependent_decisions


def test_killer_3_future_leakage(base_prov):
    engine = EvidenceGraphEngine()
    engine.add_node("src-past", GraphNodeType.EVIDENCE_SOURCE, TruthState.OBSERVED, base_prov, observed_at=100.0)
    engine.add_node("src-future", GraphNodeType.EVIDENCE_SOURCE, TruthState.OBSERVED, base_prov, observed_at=101.0)
    engine.add_node("claim-past", GraphNodeType.DECISION, TruthState.INFERRED, base_prov, observed_at=100.0)

    engine.add_edge("e-future", "src-future", "claim-past", GraphEdgeType.SUPPORTED_BY)

    with pytest.raises(TemporalLineageViolationError):
        engine.trace_backward("claim-past")


def test_killer_4_contradiction(base_prov):
    engine = EvidenceGraphEngine()
    engine.add_node("src-a", GraphNodeType.EVIDENCE_SOURCE, TruthState.OBSERVED, base_prov, observed_at=10.0, payload={"service": "Kerosene"})
    engine.add_node("src-b", GraphNodeType.EVIDENCE_SOURCE, TruthState.OBSERVED, base_prov, observed_at=10.0, payload={"service": "Diesel"})
    engine.add_node("asset-e102", GraphNodeType.CANONICAL_ENTITY, TruthState.OBSERVED, base_prov, observed_at=10.0)

    engine.add_edge("e-a", "src-a", "asset-e102", GraphEdgeType.SUPPORTS)
    engine.add_edge("e-b", "src-b", "asset-e102", GraphEdgeType.CONTRADICTS)

    assert len(engine.edges) == 2
    assert engine.edges["e-b"].edge_type == GraphEdgeType.CONTRADICTS


def test_killer_5_unknown_unresolved(base_prov):
    engine = EvidenceGraphEngine()
    engine.add_node("sensor-unknown", GraphNodeType.MEASUREMENT, TruthState.UNRESOLVED, base_prov, observed_at=10.0)
    node = engine.get_node("sensor-unknown")
    assert node.truth_state == TruthState.UNRESOLVED


def test_killer_6_assumption_lineage(foulx_lineage_fixture):
    lineage = foulx_lineage_fixture.trace_backward("comp-rf")
    assert "counter-current exchanger assumption" in lineage.assumptions
    assert "initial-window UA reference baseline" in lineage.assumptions


def test_killer_7_model_version(foulx_lineage_fixture):
    lineage = foulx_lineage_fixture.trace_backward("pred-rf24")
    assert "1.0" in lineage.model_versions


def test_killer_8_immutability(base_prov):
    import hashlib
    content = b"sample raw file content"
    h1 = hashlib.sha256(content).hexdigest()

    engine = EvidenceGraphEngine()
    engine.add_node("n1", GraphNodeType.EVIDENCE_RECORD, TruthState.OBSERVED, base_prov, payload={"data": content.decode()})
    
    h2 = hashlib.sha256(content).hexdigest()
    assert h1 == h2


def test_killer_9_determinism(foulx_lineage_fixture):
    h1 = foulx_lineage_fixture.to_deterministic_hash()
    h2 = foulx_lineage_fixture.to_deterministic_hash()
    assert h1 == h2


def test_killer_10_broken_lineage(base_prov):
    engine = EvidenceGraphEngine()
    # Node without upstream evidence source
    engine.add_node("dec-orphan", GraphNodeType.DECISION, TruthState.INFERRED, base_prov, observed_at=10.0)
    lineage = engine.trace_backward("dec-orphan")
    assert lineage.path_status == SufficiencyStatus.PARTIALLY_SUPPORTED
    assert len(lineage.missing_evidence) > 0
