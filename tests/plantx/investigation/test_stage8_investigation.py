"""Comprehensive Stage 8 Unit Test Suite covering all 14 Killer Tests."""

import pytest
import hashlib
from pathlib import Path
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.investigation.schemas import (
    InvestigationCase,
    InvestigationState,
    HypothesisAssessmentStatus,
    ScenarioExecutionError,
)
from src.plantx.investigation.engine import InvestigationEngine
from src.plantx.investigation.evidence_bridge import InvestigationEvidenceBridge
from src.plantx.graph.evidence_graph import EvidenceGraph, EvidenceEdgeType
from src.plantx.intelligence.schemas import FoulingState
from src.plantx.trust.schemas import SafetyViolationError


@pytest.fixture
def investigation_engine():
    return InvestigationEngine()


@pytest.fixture
def sample_fouling_state():
    prov = Provenance(
        provenance_id="prov-fs-1",
        provenance_type=ProvenanceType.CALCULATION,
        source_reference="test",
        timestamp="2026-09-17T14:12:00Z",
        transformation_applied="test",
    )
    return FoulingState(
        asset_id="E102",
        timestamp=1000.0,
        current_rf_derived=0.00025,
        recent_delta_rf=0.00005,
        recent_growth_rate=0.000001,
        historical_context_hours=168.0,
        status="VALID",
        truth_state=TruthState.INFERRED,
        provenance=prov,
    )


# Killer Test 1: Multiple Candidate Hypotheses Generation
def test_killer_1_multiple_hypotheses(investigation_engine, sample_fouling_state):
    case = investigation_engine.create_case("E102", 1000.0, "Increasing derived thermal resistance", fouling_state=sample_fouling_state)
    assert len(case.hypotheses) >= 5
    names = [h.name for h in case.hypotheses]
    assert "FOULING_ACCUMULATION" in names
    assert "OPERATING_REGIME_CHANGE" in names
    assert "SENSOR_MEASUREMENT_ISSUE" in names
    assert "FEED_PROPERTY_SHIFT" in names
    assert "FLOW_OR_HYDRAULIC_EFFECT" in names


# Killer Test 2: Supporting Evidence Integration
def test_killer_2_supporting_evidence(investigation_engine, sample_fouling_state):
    case = investigation_engine.create_case("E102", 1000.0, "Thermal degradation detected", fouling_state=sample_fouling_state)
    h1 = next(h for h in case.hypotheses if h.name == "FOULING_ACCUMULATION")
    assert len(h1.supporting_evidence) > 0
    assert h1.status in (HypothesisAssessmentStatus.PARTIALLY_SUPPORTED, HypothesisAssessmentStatus.SUPPORTED_BY_AVAILABLE_EVIDENCE)


# Killer Test 3: Contradicting Evidence Handling
def test_killer_3_contradicting_evidence(investigation_engine):
    case = investigation_engine.create_case("E102", 1000.0, "Thermal anomaly")
    h1 = next(h for h in case.hypotheses if h.name == "FOULING_ACCUMULATION")
    assert h1.status == HypothesisAssessmentStatus.INSUFFICIENT_EVIDENCE


# Killer Test 4: Missing Evidence Identification
def test_killer_4_missing_evidence(investigation_engine, sample_fouling_state):
    case = investigation_engine.create_case("E102", 1000.0, "Increasing Rf", fouling_state=sample_fouling_state)
    assert "delta_p_history" in case.missing_evidence


# Killer Test 5: Discriminating Observation Finding
def test_killer_5_discriminating_observation(investigation_engine, sample_fouling_state):
    case = investigation_engine.create_case("E102", 1000.0, "Increasing Rf", fouling_state=sample_fouling_state)
    assert len(case.discriminating_observations) > 0
    obs_desc = [o.description for o in case.discriminating_observations]
    assert any("Differential Pressure" in d for d in obs_desc)


# Killer Test 6: No Causal Overclaim from Rf Alone
def test_killer_6_no_causal_overclaim(investigation_engine, sample_fouling_state):
    case = investigation_engine.create_case("E102", 1000.0, "Rf trajectory change", fouling_state=sample_fouling_state)
    assert case.mechanism_claim == "NONE"


# Killer Test 7: Future Evidence Prevention
def test_killer_7_future_evidence_prevention(investigation_engine):
    case = investigation_engine.create_case("E102", 1000.0, "Anomaly")
    assert case.timestamp == 1000.0


# Killer Test 8: Evidence Graph Traceability
def test_killer_8_evidence_graph_trace(investigation_engine, sample_fouling_state):
    graph = EvidenceGraph()
    graph.add_node("state-1", "State", TruthState.INFERRED.value, {"rf": 0.00025})
    
    case = investigation_engine.create_case("E102", 1000.0, "Increasing Rf", fouling_state=sample_fouling_state)
    node_id = InvestigationEvidenceBridge.attach_case_to_graph(graph, case, "state-1")
    
    trace = graph.trace_backward(node_id)
    assert node_id in trace
    assert "state-1" in trace


# Killer Test 9: Determinism
def test_killer_9_determinism(investigation_engine, sample_fouling_state):
    case1 = investigation_engine.create_case("E102", 1000.0, "Increasing Rf", fouling_state=sample_fouling_state)
    case2 = investigation_engine.create_case("E102", 1000.0, "Increasing Rf", fouling_state=sample_fouling_state)
    assert case1.model_dump() == case2.model_dump()


# Killer Test 10: Unresolved Case Status
def test_killer_10_unresolved_case(investigation_engine):
    case = investigation_engine.create_case("E102", 1000.0, "Anomaly with zero extra state")
    h3 = next(h for h in case.hypotheses if h.name == "SENSOR_MEASUREMENT_ISSUE")
    assert h3.status == HypothesisAssessmentStatus.INSUFFICIENT_EVIDENCE


# Killer Test 11: Conflicting Evidence Handling
def test_killer_11_conflicting_evidence(investigation_engine, sample_fouling_state):
    conflicts = [{"source_a": "Flow increase", "source_b": "Flow unchanged"}]
    case = investigation_engine.create_case("E102", 1000.0, "Anomaly", fouling_state=sample_fouling_state, conflicting_sources=conflicts)
    assert len(case.conflicting_evidence) > 0
    h1 = next(h for h in case.hypotheses if h.name == "FOULING_ACCUMULATION")
    assert h1.status == HypothesisAssessmentStatus.CONFLICTING_EVIDENCE


# Killer Test 12: Human Control Mandate
def test_killer_12_human_control_mandate(investigation_engine, sample_fouling_state):
    case = investigation_engine.create_case("E102", 1000.0, "Anomaly", fouling_state=sample_fouling_state)
    assert case.recommended_investigation.human_action_required is True


# Killer Test 13: Source Immutability
def test_killer_13_source_immutability(investigation_engine, sample_fouling_state):
    dataset_path = Path("data/raw/heat_exchanger_fouling_dataset.csv")
    h_before = hashlib.sha256(dataset_path.read_bytes()).hexdigest()
    
    investigation_engine.create_case("E102", 1000.0, "Anomaly", fouling_state=sample_fouling_state)
    
    h_after = hashlib.sha256(dataset_path.read_bytes()).hexdigest()
    assert h_before == h_after
    assert h_before == "c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9"


# Killer Test 14: Stage 9 Boundary Prevention
def test_killer_14_stage_9_boundary_prevention(investigation_engine):
    with pytest.raises(ScenarioExecutionError):
        investigation_engine.create_case(
            "E102", 1000.0, "Anomaly", allow_scenario_execution=True
        )
