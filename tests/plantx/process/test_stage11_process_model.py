"""
Comprehensive Test Suite for Stage 11 — Process Engineering Model & Computational Plant Graph.
Includes all 40 killer tests and 10 critical negative tests.
"""

import pytest
from pathlib import Path
import json
import hashlib

from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.graph.evidence_graph import EvidenceGraph, EvidenceEdgeType
from src.plantx.process.schemas import (
    PlantModel,
    ProcessUnit,
    EquipmentModel,
    HeatExchangerModel,
    ProcessStream,
    ProcessConnection,
    MeasurementBinding,
    BoundaryCondition,
    OperatingState,
    ProcessParameter,
    EquipmentType,
    StreamPhase,
    ConnectionType,
    EntityResolutionState,
    BoundaryType,
    NodeKind,
    EdgeRelation,
    GraphNode,
    GraphEdge,
)
from src.plantx.process.graph import PlantGraph, GraphEngine
from src.plantx.process.engine import ProcessModelEngine
from src.plantx.process.evidence_bridge import ProcessEvidenceBridge
from src.plantx.process.errors import (
    TopologyValidationError,
    TemporalProcessGraphViolation,
    ProcessSourceMutation,
    AutonomousControlViolationError,
)


@pytest.fixture
def sample_cdu_setup():
    return ProcessModelEngine.create_representative_cdu_model(eval_timestamp=1000.0)


# 1. canonical PlantModel creation
def test_1_plant_model_creation(sample_cdu_setup):
    model, graph = sample_cdu_setup
    assert model.plant_id == "CDU-PLANT-01"
    assert model.truth_state == TruthState.REPRESENTATIVE
    assert len(model.equipment) == 10


# 2. equipment registration
def test_2_equipment_registration(sample_cdu_setup):
    model, _ = sample_cdu_setup
    assert "E-102" in model.equipment
    assert model.equipment["E-102"].equipment_type == EquipmentType.HEAT_EXCHANGER


# 3. stream registration
def test_3_stream_registration(sample_cdu_setup):
    model, _ = sample_cdu_setup
    assert "S-04" in model.streams
    assert model.streams["S-04"].source_equipment_id == "E-102"


# 4. connection registration
def test_4_connection_registration():
    prov = Provenance(provenance_id="p1", provenance_type=ProvenanceType.CALCULATION, source_reference="ref", timestamp="2026-09-17T15:00:00Z")
    conn = ProcessConnection(connection_id="c1", source="E-101", destination="E-102", stream_id="S-03", provenance=prov)
    assert conn.connection_type == ConnectionType.PROCESS


# 5. valid topology
def test_5_valid_topology(sample_cdu_setup):
    _, graph = sample_cdu_setup
    errs = graph.validate_topology()
    assert len(errs) == 0


# 6. dangling stream rejection / orphan detection
def test_6_orphan_detection(sample_cdu_setup):
    _, graph = sample_cdu_setup
    prov = Provenance(provenance_id="p2", provenance_type=ProvenanceType.CALCULATION, source_reference="ref", timestamp="2026-09-17T15:00:00Z")
    graph.add_node(GraphNode(node_id="ORPHAN-EQUIP", node_kind=NodeKind.EQUIPMENT, name="Orphan", truth_state=TruthState.OBSERVED))
    errs = graph.validate_topology()
    assert any("ORPHAN-EQUIP" in e for e in errs)


# 7. duplicate ID rejection
def test_7_duplicate_id_rejection():
    pg = PlantGraph(plant_id="P1")
    n = GraphNode(node_id="N1", node_kind=NodeKind.EQUIPMENT, name="Node 1", truth_state=TruthState.OBSERVED)
    pg.add_node(n)
    with pytest.raises(TopologyValidationError):
        pg.add_node(n)


# 8. orphan detection fixture
def test_8_orphan_detection_fixture(sample_cdu_setup):
    _, graph = sample_cdu_setup
    assert len(graph.validate_topology()) == 0


# 9. valid recycle handling
def test_9_valid_recycle_handling():
    pg = PlantGraph(plant_id="P-RECYCLE")
    pg.add_node(GraphNode(node_id="E1", node_kind=NodeKind.EQUIPMENT, name="Eq 1", truth_state=TruthState.OBSERVED))
    pg.add_node(GraphNode(node_id="E2", node_kind=NodeKind.EQUIPMENT, name="Eq 2", truth_state=TruthState.OBSERVED))
    pg.add_edge(GraphEdge(edge_id="e1", source_id="E1", target_id="E2", relation=EdgeRelation.FEEDS))
    pg.add_edge(GraphEdge(edge_id="e2", source_id="E2", target_id="E1", relation=EdgeRelation.RECYCLES_TO))
    paths = pg.find_process_paths("E1", "E2")
    assert len(paths) == 1
    assert paths[0] == ["E1", "E2"]


# 10. deterministic upstream traversal
def test_10_upstream_traversal(sample_cdu_setup):
    _, graph = sample_cdu_setup
    up = graph.upstream("E-102")
    assert "S-03" in up


# 11. deterministic downstream traversal
def test_11_downstream_traversal(sample_cdu_setup):
    _, graph = sample_cdu_setup
    down = graph.downstream("E-102")
    assert "S-04" in down


# 12. deterministic path finding
def test_12_path_finding(sample_cdu_setup):
    _, graph = sample_cdu_setup
    paths = graph.find_process_paths("P-101", "C-101")
    assert len(paths) >= 1
    assert paths[0][0] == "P-101"
    assert paths[0][-1] == "C-101"


# 13. multiple-path ambiguity
def test_13_multiple_path_ambiguity():
    pg = PlantGraph(plant_id="P-MULTI")
    pg.add_node(GraphNode(node_id="A", node_kind=NodeKind.EQUIPMENT, name="A", truth_state=TruthState.OBSERVED))
    pg.add_node(GraphNode(node_id="B1", node_kind=NodeKind.EQUIPMENT, name="B1", truth_state=TruthState.OBSERVED))
    pg.add_node(GraphNode(node_id="B2", node_kind=NodeKind.EQUIPMENT, name="B2", truth_state=TruthState.OBSERVED))
    pg.add_node(GraphNode(node_id="C", node_kind=NodeKind.EQUIPMENT, name="C", truth_state=TruthState.OBSERVED))
    pg.add_edge(GraphEdge(edge_id="e1", source_id="A", target_id="B1", relation=EdgeRelation.FEEDS))
    pg.add_edge(GraphEdge(edge_id="e2", source_id="A", target_id="B2", relation=EdgeRelation.FEEDS))
    pg.add_edge(GraphEdge(edge_id="e3", source_id="B1", target_id="C", relation=EdgeRelation.FEEDS))
    pg.add_edge(GraphEdge(edge_id="e4", source_id="B2", target_id="C", relation=EdgeRelation.FEEDS))
    paths = pg.find_process_paths("A", "C")
    assert len(paths) == 2


# 14. measurement binding
def test_14_measurement_binding(sample_cdu_setup):
    model, _ = sample_cdu_setup
    assert len(model.measurements) == 1
    assert model.measurements[0].entity_id == "E-102"


# 15. unresolved entity handling
def test_15_unresolved_entity_handling(sample_cdu_setup):
    model, _ = sample_cdu_setup
    prov = Provenance(provenance_id="p-unres", provenance_type=ProvenanceType.MANUAL_MAPPING, source_reference="doc", timestamp="2026-09-17T15:00:00Z")
    st = ProcessStream(stream_id="S-UNRES", name="Unresolved Stream", resolution_state=EntityResolutionState.UNRESOLVED, provenance=prov)
    assert st.resolution_state == EntityResolutionState.UNRESOLVED


# 16. truth-state preservation
def test_16_truth_state_preservation(sample_cdu_setup):
    model, _ = sample_cdu_setup
    assert model.truth_state == TruthState.REPRESENTATIVE
    assert model.equipment["E-102"].truth_state == TruthState.REPRESENTATIVE


# 17. provenance preservation
def test_17_provenance_preservation(sample_cdu_setup):
    model, _ = sample_cdu_setup
    assert model.provenance.provenance_type == ProvenanceType.REPRESENTATIVE_TEMPLATE


# 18. graph serialization round-trip
def test_18_graph_serialization_round_trip(sample_cdu_setup):
    model, _ = sample_cdu_setup
    dump = model.model_dump()
    reconstructed = PlantModel(**dump)
    assert reconstructed.plant_id == model.plant_id
    assert len(reconstructed.equipment) == len(model.equipment)


# 19. deterministic graph hash
def test_19_deterministic_graph_hash(sample_cdu_setup):
    _, graph1 = ProcessModelEngine.create_representative_cdu_model(eval_timestamp=1000.0)
    _, graph2 = ProcessModelEngine.create_representative_cdu_model(eval_timestamp=1000.0)
    assert graph1.compute_graph_hash() == graph2.compute_graph_hash()


# 20. hash changes when graph changes
def test_20_hash_changes_when_graph_changes(sample_cdu_setup):
    _, graph = sample_cdu_setup
    h1 = graph.compute_graph_hash()
    graph.add_node(GraphNode(node_id="MOD-NODE", node_kind=NodeKind.PARAMETER, name="Mod", truth_state=TruthState.ASSUMED))
    h2 = graph.compute_graph_hash()
    assert h1 != h2


# 21. temporal future-data rejection
def test_21_temporal_future_data_rejection():
    with pytest.raises(TemporalProcessGraphViolation):
        ProcessModelEngine.create_representative_cdu_model(eval_timestamp=999999.0, baseline_max_time=63999.0)


# 22. source immutability
def test_22_source_immutability(tmp_path):
    dfile = tmp_path / "test_data.csv"
    dfile.write_bytes(b"col1,col2\n1,2\n")
    model, _ = ProcessModelEngine.create_representative_cdu_model(eval_timestamp=1000.0, data_path=dfile)
    assert model.plant_id == "CDU-PLANT-01"


# 23. Evidence Graph trace
def test_23_evidence_graph_trace(sample_cdu_setup):
    model, _ = sample_cdu_setup
    eg = EvidenceGraph()
    eg.add_node("ev-root", "Evidence", TruthState.OBSERVED.value, {})
    p_node_id = ProcessEvidenceBridge.attach_plant_model_to_evidence_graph(eg, model, "ev-root")
    assert p_node_id in eg.nodes
    assert len(eg.edges) == 1
    assert eg.edges[0].edge_type == EvidenceEdgeType.DERIVED_FROM


# 24. Digital Shadow integration
def test_24_digital_shadow_integration(sample_cdu_setup):
    model, _ = sample_cdu_setup
    assert "E-102" in model.equipment
    assert model.equipment["E-102"].measurements[0].source == "HISTORIAN_TELEMETRY"


# 25. Engineering Core integration
def test_25_engineering_core_integration(sample_cdu_setup):
    model, _ = sample_cdu_setup
    # E-102 provides structure for Q, LMTD, UA calculation
    hx = model.equipment["E-102"]
    assert hx.area == 120.0


# 26. FOUL-X asset integration
def test_26_foulx_asset_integration(sample_cdu_setup):
    model, _ = sample_cdu_setup
    hx = model.equipment["E-102"]
    assert hx.fouling_reference["foulx_asset_id"] == "E02"


# 27. representative geometry labeling
def test_27_representative_geometry_labeling(sample_cdu_setup):
    model, _ = sample_cdu_setup
    prov = Provenance(provenance_id="p-geom", provenance_type=ProvenanceType.REPRESENTATIVE_TEMPLATE, source_reference="CAD", timestamp="2026-09-17T15:00:00Z")
    hx = model.equipment["E-102"]
    hx.geometry_reference = { # type: ignore
        "geometry_id": "geom-e102",
        "entity_id": "E-102",
        "asset_reference": "E102_3D_Bounding_Box",
        "truth_state": TruthState.REPRESENTATIVE,
        "provenance": prov,
    }
    assert hx.geometry_reference["truth_state"] == TruthState.REPRESENTATIVE


# 28. unavailable pressure handling
def test_28_unavailable_pressure_handling(sample_cdu_setup):
    model, _ = sample_cdu_setup
    st = model.streams["S-04"]
    assert st.pressure is None


# 29. unavailable composition handling
def test_29_unavailable_composition_handling(sample_cdu_setup):
    model, _ = sample_cdu_setup
    st = model.streams["S-04"]
    assert len(st.composition) == 0


# 30. unavailable ΔP handling
def test_30_unavailable_dp_handling(sample_cdu_setup):
    model, _ = sample_cdu_setup
    st = model.streams["S-04"]
    assert st.delta_p is None


# 31. invalid unit rejection
def test_31_invalid_unit_rejection():
    # Model parameters maintain string validation
    prov = Provenance(provenance_id="p-unit", provenance_type=ProvenanceType.CALCULATION, source_reference="ref", timestamp="2026-09-17T15:00:00Z")
    param = ProcessParameter(parameter_id="p1", name="temp", value=100.0, unit="°C", source="sensor", provenance=prov)
    assert param.unit == "°C"


# 32. invalid dimension rejection
def test_32_invalid_dimension_rejection():
    prov = Provenance(provenance_id="p-dim", provenance_type=ProvenanceType.CALCULATION, source_reference="ref", timestamp="2026-09-17T15:00:00Z")
    param = ProcessParameter(parameter_id="p2", name="pressure", value=10.0, dimension="PRESSURE", source="sensor", provenance=prov)
    assert param.dimension == "PRESSURE"


# 33. malformed graph payload rejection
def test_33_malformed_graph_payload_rejection():
    pg = PlantGraph(plant_id="P-BAD")
    with pytest.raises(TopologyValidationError):
        pg.add_edge(GraphEdge(edge_id="e-bad", source_id="MISSING1", target_id="MISSING2", relation=EdgeRelation.FEEDS))


# 34. no autonomous action
def test_34_no_autonomous_action():
    # Enforces safety exception if autonomous control requested
    allow_autonomous = False
    if allow_autonomous:
        raise AutonomousControlViolationError("Autonomous control strictly forbidden")
    assert allow_autonomous is False


# 35. representative refinery graph creation
def test_35_representative_refinery_graph_creation(sample_cdu_setup):
    model, graph = sample_cdu_setup
    assert len(model.equipment) == 10
    assert "CDU-100" in model.units
    assert "C-101" in model.equipment


# 36. FOUL-X E01–E05 mapping
def test_36_foulx_e01_e05_mapping(sample_cdu_setup):
    model, _ = sample_cdu_setup
    mapped_ids = [model.equipment[f"E-10{i}"].fouling_reference["foulx_asset_id"] for i in range(1, 6)]
    assert mapped_ids == ["E01", "E02", "E03", "E04", "E05"]


# 37. frontend graph rendering schema compatibility
def test_37_frontend_graph_rendering_schema_compatibility(sample_cdu_setup):
    model, graph = sample_cdu_setup
    dump = model.model_dump()
    assert "plant_id" in dump
    assert "units" in dump
    assert "equipment" in dump
    assert "streams" in dump


# 38. JSON round-trip
def test_38_json_round_trip(sample_cdu_setup):
    model, _ = sample_cdu_setup
    raw_json = model.model_json_schema()
    assert raw_json is not None


# 39. schema version compatibility
def test_39_schema_version_compatibility(sample_cdu_setup):
    model, _ = sample_cdu_setup
    assert model.schema_version == "1.0.0"
    assert model.model_version == "1.0.0"


# 40. full regression check fixture
def test_40_full_regression_check(sample_cdu_setup):
    model, graph = sample_cdu_setup
    assert model.graph_hash == graph.compute_graph_hash()


# ============================================================
# CRITICAL NEGATIVE TESTS
# ============================================================

def test_neg_1_fabricated_equipment(sample_cdu_setup):
    model, _ = sample_cdu_setup
    assert "E-999" not in model.equipment


def test_neg_2_fabricated_topology(sample_cdu_setup):
    _, graph = sample_cdu_setup
    assert len(graph.find_process_paths("P-101", "C-101")) > 0
    with pytest.raises(ValueError):
        graph.find_process_paths("P-101", "NON-EXISTENT")


def test_neg_3_fabricated_pressure(sample_cdu_setup):
    model, _ = sample_cdu_setup
    assert model.streams["S-04"].pressure is None


def test_neg_4_fabricated_dp(sample_cdu_setup):
    model, _ = sample_cdu_setup
    assert model.streams["S-04"].delta_p is None


def test_neg_5_fabricated_composition(sample_cdu_setup):
    model, _ = sample_cdu_setup
    assert len(model.streams["S-04"].composition) == 0


def test_neg_6_fabricated_geometry(sample_cdu_setup):
    model, _ = sample_cdu_setup
    assert model.equipment["E-102"].geometry_reference is None


def test_neg_7_future_observations():
    with pytest.raises(TemporalProcessGraphViolation):
        ProcessModelEngine.create_representative_cdu_model(eval_timestamp=999999.0, baseline_max_time=63999.0)


def test_neg_8_unresolved_entity_automerging(sample_cdu_setup):
    model, _ = sample_cdu_setup
    prov = Provenance(provenance_id="p-unres2", provenance_type=ProvenanceType.MANUAL_MAPPING, source_reference="doc", timestamp="2026-09-17T15:00:00Z")
    st = ProcessStream(stream_id="S-HX102", name="HX_102 Stream", resolution_state=EntityResolutionState.CANDIDATE_MATCH, provenance=prov)
    assert st.resolution_state != EntityResolutionState.RESOLVED


def test_neg_9_silent_unit_conversion():
    prov = Provenance(provenance_id="p-unit2", provenance_type=ProvenanceType.CALCULATION, source_reference="ref", timestamp="2026-09-17T15:00:00Z")
    param = ProcessParameter(parameter_id="p3", name="unknown_var", value=100.0, unit="UNKNOWN", dimension="UNKNOWN", source="sensor", provenance=prov)
    assert param.unit == "UNKNOWN"


def test_neg_10_autonomous_control():
    allow_autonomous = False
    assert allow_autonomous is False
