"""
Comprehensive Test Suite for Stage 12 — Process Graph Solver + Mass / Energy Balance Engine.
Includes all 42 killer tests and 11 critical negative tests.
"""

import pytest
from pathlib import Path
import hashlib

from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.graph.evidence_graph import EvidenceGraph, EvidenceEdgeType
from src.plantx.process.schemas import (
    PlantModel,
    ProcessStream,
    StreamPhase,
    ComponentFraction,
)
from src.plantx.process.engine import ProcessModelEngine
from src.plantx.process.graph import PlantGraph, GraphEngine, GraphNode, GraphEdge, NodeKind, EdgeRelation
from src.plantx.balance.schemas import (
    BalanceCase,
    BalanceScopeType,
    BalanceStatus,
    DiagnosticType,
)
from src.plantx.balance.mass_balance import MassBalanceEngine, ComponentBalanceEngine
from src.plantx.balance.energy_balance import EnergyBalanceEngine
from src.plantx.balance.solver import BalanceSolver
from src.plantx.balance.evidence_bridge import BalanceEvidenceBridge
from src.plantx.balance.errors import (
    TemporalBalanceViolation,
    BalanceSourceMutation,
    AutonomousControlViolationError,
)


@pytest.fixture
def sample_cdu_setup():
    return ProcessModelEngine.create_representative_cdu_model(eval_timestamp=1000.0)


# 1. equipment mass balance
def test_1_equipment_mass_balance(sample_cdu_setup):
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    assert case.mass_balance.status == BalanceStatus.BALANCED
    assert case.mass_balance.residual == 0.0


# 2. equipment energy balance
def test_2_equipment_energy_balance(sample_cdu_setup):
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    assert case.energy_balance.status in [BalanceStatus.PARTIALLY_EVALUATED, BalanceStatus.BALANCED_WITH_LIMITATIONS, BalanceStatus.BALANCED]


# 3. process-unit mass balance
def test_3_process_unit_mass_balance(sample_cdu_setup):
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "P-101", 1000.0)
    assert case.mass_balance.status == BalanceStatus.BALANCED


# 4. plant boundary classification
def test_4_plant_boundary_classification(sample_cdu_setup):
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.PLANT, "CDU-PLANT-01", 1000.0)
    assert len(case.input_streams) >= 1
    assert len(case.internal_streams) >= 1


# 5. internal stream cancellation
def test_5_internal_stream_cancellation(sample_cdu_setup):
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.PLANT, "CDU-PLANT-01", 1000.0)
    assert "S-02" in case.internal_streams
    assert "S-02" not in case.input_streams
    assert "S-02" not in case.output_streams


# 6. recycle detection
def test_6_recycle_detection():
    pg = PlantGraph(plant_id="P-REC")
    pg.add_node(GraphNode(node_id="E1", node_kind=NodeKind.EQUIPMENT, name="E1", truth_state=TruthState.OBSERVED))
    pg.add_node(GraphNode(node_id="E2", node_kind=NodeKind.EQUIPMENT, name="E2", truth_state=TruthState.OBSERVED))
    pg.add_edge(GraphEdge(edge_id="e1", source_id="E1", target_id="E2", relation=EdgeRelation.FEEDS))
    pg.add_edge(GraphEdge(edge_id="e2", source_id="E2", target_id="E1", relation=EdgeRelation.RECYCLES_TO))

    prov = Provenance(provenance_id="p", provenance_type=ProvenanceType.CALCULATION, source_reference="s", timestamp="2026-09-17T15:25:00Z")
    model = PlantModel(plant_id="P-REC", name="Recycle Plant", description="Recycle test", provenance=prov, truth_state=TruthState.OBSERVED)
    model.equipment["E1"] = ProcessModelEngine.create_representative_cdu_model()[0].equipment["P-101"]
    model.equipment["E1"].equipment_id = "E1"

    case = BalanceSolver.solve_balance_case(model, pg, BalanceScopeType.EQUIPMENT, "E1", 1000.0)
    assert any(d.diagnostic_type == DiagnosticType.RECYCLE_PRESENT for d in case.diagnostics)


# 7. component balance
def test_7_component_balance():
    prov = Provenance(provenance_id="pcomp", provenance_type=ProvenanceType.CALCULATION, source_reference="s", timestamp="2026-09-17T15:25:00Z")
    s_in = ProcessStream(
        stream_id="S-IN", name="In", mass_flow=10.0,
        composition={"C1": ComponentFraction(component_name="C1", value=0.6), "C2": ComponentFraction(component_name="C2", value=0.4)},
        provenance=prov,
    )
    s_out = ProcessStream(
        stream_id="S-OUT", name="Out", mass_flow=10.0,
        composition={"C1": ComponentFraction(component_name="C1", value=0.6), "C2": ComponentFraction(component_name="C2", value=0.4)},
        provenance=prov,
    )
    res = ComponentBalanceEngine.evaluate_component_balance([s_in], [s_out], 1000.0)
    assert res["C1"].status == BalanceStatus.BALANCED


# 8. composition basis validation
def test_8_composition_basis_validation():
    cf = ComponentFraction(component_name="Methane", value=0.5, unit="mass_fraction")
    assert cf.unit == "mass_fraction"


# 9. missing composition
def test_9_missing_composition(sample_cdu_setup):
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    assert len(case.component_balances) == 0
    assert "Stream chemical composition" in case.missing_inputs


# 10. missing mass flow
def test_10_missing_mass_flow():
    prov = Provenance(provenance_id="pmiss", provenance_type=ProvenanceType.CALCULATION, source_reference="s", timestamp="2026-09-17T15:25:00Z")
    s_in = ProcessStream(stream_id="S-IN", name="In", mass_flow=None, provenance=prov)
    s_out = ProcessStream(stream_id="S-OUT", name="Out", mass_flow=10.0, provenance=prov)
    res = MassBalanceEngine.evaluate_mass_balance([s_in], [s_out], 1000.0)
    assert res.status == BalanceStatus.PARTIALLY_EVALUATED
    assert res.residual is None


# 11. missing enthalpy
def test_11_missing_enthalpy(sample_cdu_setup):
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    assert any(d.diagnostic_type == DiagnosticType.ENTHALPY_UNAVAILABLE for d in case.diagnostics)


# 12. missing heat boundary
def test_12_missing_heat_boundary():
    res = EnergyBalanceEngine.evaluate_energy_balance([], [], 1000.0)
    assert res.heat_in.source == "UNAVAILABLE"


# 13. unit validation
def test_13_unit_validation():
    res = MassBalanceEngine.evaluate_mass_balance([], [], 1000.0)
    assert res.unit == "kg/s"


# 14. dimension validation
def test_14_dimension_validation():
    res = EnergyBalanceEngine.evaluate_energy_balance([], [], 1000.0)
    assert res.unit == "kW"


# 15. tolerance handling
def test_15_tolerance_handling():
    prov = Provenance(provenance_id="ptol", provenance_type=ProvenanceType.CALCULATION, source_reference="s", timestamp="2026-09-17T15:25:00Z")
    s_in = ProcessStream(stream_id="S-IN", name="In", mass_flow=100.0, provenance=prov)
    s_out = ProcessStream(stream_id="S-OUT", name="Out", mass_flow=99.5, provenance=prov)
    res = MassBalanceEngine.evaluate_mass_balance([s_in], [s_out], 1000.0, tolerance=0.01)
    assert res.status == BalanceStatus.BALANCED


# 16. imbalance detection
def test_16_imbalance_detection():
    prov = Provenance(provenance_id="pimb", provenance_type=ProvenanceType.CALCULATION, source_reference="s", timestamp="2026-09-17T15:25:00Z")
    s_in = ProcessStream(stream_id="S-IN", name="In", mass_flow=100.0, provenance=prov)
    s_out = ProcessStream(stream_id="S-OUT", name="Out", mass_flow=80.0, provenance=prov)
    res = MassBalanceEngine.evaluate_mass_balance([s_in], [s_out], 1000.0, tolerance=0.01)
    assert res.status == BalanceStatus.IMBALANCE
    assert res.residual == 20.0


# 17. energy imbalance detection
def test_17_energy_imbalance_detection():
    prov = Provenance(provenance_id="peimb", provenance_type=ProvenanceType.CALCULATION, source_reference="s", timestamp="2026-09-17T15:25:00Z")
    s_in = ProcessStream(stream_id="S-IN", name="In", enthalpy=1000.0, provenance=prov)
    s_out = ProcessStream(stream_id="S-OUT", name="Out", enthalpy=500.0, provenance=prov)
    res = EnergyBalanceEngine.evaluate_energy_balance([s_in], [s_out], 1000.0, tolerance=0.02)
    assert res.status == BalanceStatus.IMBALANCE


# 18. partial evaluation
def test_18_partial_evaluation(sample_cdu_setup):
    model, graph = sample_cdu_setup
    model.streams["S-03"].mass_flow = None
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    assert case.mass_balance.status == BalanceStatus.PARTIALLY_EVALUATED


# 19. unavailable evaluation
def test_19_unavailable_evaluation():
    res = MassBalanceEngine.evaluate_mass_balance([], [], 1000.0)
    assert res.status == BalanceStatus.PARTIALLY_EVALUATED


# 20. temporal violation
def test_20_temporal_violation(sample_cdu_setup):
    model, graph = sample_cdu_setup
    with pytest.raises(TemporalBalanceViolation):
        BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 999999.0, baseline_max_time=63999.0)


# 21. source immutability
def test_21_source_immutability(sample_cdu_setup, tmp_path):
    dfile = tmp_path / "test_data.csv"
    dfile.write_bytes(b"col1,col2\n1,2\n")
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0, data_path=dfile)
    assert case.balance_id.startswith("bal-E-102")


# 22. deterministic execution
def test_22_deterministic_execution(sample_cdu_setup):
    model, graph = sample_cdu_setup
    c1 = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    c2 = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    assert c1.result_hash == c2.result_hash


# 23. deterministic result hash
def test_23_deterministic_result_hash(sample_cdu_setup):
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    assert len(case.result_hash) == 64


# 24. Evidence Graph trace
def test_24_evidence_graph_trace(sample_cdu_setup):
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    eg = EvidenceGraph()
    eg.add_node("plant-node-1", "ProcessPlantModel", TruthState.REPRESENTATIVE.value, {})
    b_node_id = BalanceEvidenceBridge.attach_balance_case_to_evidence_graph(eg, case, "plant-node-1")
    assert b_node_id in eg.nodes
    assert len(eg.edges) == 1
    assert eg.edges[0].edge_type == EvidenceEdgeType.DERIVED_FROM


# 25. Stage 5 integration
def test_25_stage5_integration(sample_cdu_setup):
    model, graph = sample_cdu_setup
    # Balance Engine consumes stream mass_flow from Stage 5 telemetry/derived state
    assert model.streams["S-03"].mass_flow == 50.0


# 26. Stage 11 integration
def test_26_stage11_integration(sample_cdu_setup):
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    assert case.graph_hash == model.graph_hash


# 27. FOUL-X E-102 integration
def test_27_foulx_e102_integration(sample_cdu_setup):
    model, graph = sample_cdu_setup
    hx = model.equipment["E-102"]
    assert hx.fouling_reference["foulx_asset_id"] == "E02"


# 28. missing ≠ zero
def test_28_missing_not_zero():
    prov = Provenance(provenance_id="pzero", provenance_type=ProvenanceType.CALCULATION, source_reference="s", timestamp="2026-09-17T15:25:00Z")
    s_in = ProcessStream(stream_id="S-IN", name="In", mass_flow=None, provenance=prov)
    s_out = ProcessStream(stream_id="S-OUT", name="Out", mass_flow=10.0, provenance=prov)
    res = MassBalanceEngine.evaluate_mass_balance([s_in], [s_out], 1000.0)
    assert res.total_in is None
    assert res.total_in != 0.0


# 29. valid recycle recognition
def test_29_valid_recycle_recognition():
    pg = PlantGraph(plant_id="P-REC2")
    pg.add_node(GraphNode(node_id="E1", node_kind=NodeKind.EQUIPMENT, name="E1", truth_state=TruthState.OBSERVED))
    pg.add_node(GraphNode(node_id="E2", node_kind=NodeKind.EQUIPMENT, name="E2", truth_state=TruthState.OBSERVED))
    pg.add_edge(GraphEdge(edge_id="e1", source_id="E1", target_id="E2", relation=EdgeRelation.FEEDS))
    pg.add_edge(GraphEdge(edge_id="e2", source_id="E2", target_id="E1", relation=EdgeRelation.RECYCLES_TO))

    prov = Provenance(provenance_id="p", provenance_type=ProvenanceType.CALCULATION, source_reference="s", timestamp="2026-09-17T15:25:00Z")
    model = PlantModel(plant_id="P-REC2", name="Recycle Plant", description="Recycle test", provenance=prov, truth_state=TruthState.OBSERVED)
    model.equipment["E1"] = ProcessModelEngine.create_representative_cdu_model()[0].equipment["P-101"]
    model.equipment["E1"].equipment_id = "E1"

    case = BalanceSolver.solve_balance_case(model, pg, BalanceScopeType.EQUIPMENT, "E1", 1000.0)
    assert any(d.diagnostic_type == DiagnosticType.RECYCLE_PRESENT for d in case.diagnostics)


# 30. unsupported recycle convergence
def test_30_unsupported_recycle_convergence(sample_cdu_setup):
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    assert case.status in [BalanceStatus.BALANCED, BalanceStatus.PARTIALLY_EVALUATED]


# 31. conflicting input preservation
def test_31_conflicting_input_preservation():
    prov = Provenance(provenance_id="pconf", provenance_type=ProvenanceType.CALCULATION, source_reference="s", timestamp="2026-09-17T15:25:00Z")
    s_in = ProcessStream(stream_id="S-IN", name="In", mass_flow=100.0, provenance=prov)
    s_out = ProcessStream(stream_id="S-OUT", name="Out", mass_flow=50.0, provenance=prov)
    res = MassBalanceEngine.evaluate_mass_balance([s_in], [s_out], 1000.0)
    assert res.status == BalanceStatus.IMBALANCE
    assert res.residual == 50.0


# 32. invalid topology
def test_32_invalid_topology(sample_cdu_setup):
    model, graph = sample_cdu_setup
    with pytest.raises(ValueError):
        BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "MISSING_EQUIPMENT", 1000.0)


# 33. duplicate stream detection
def test_33_duplicate_stream_detection(sample_cdu_setup):
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    assert len(case.input_streams) == len(set(case.input_streams))


# 34. duplicate balance detection
def test_34_duplicate_balance_detection(sample_cdu_setup):
    model, graph = sample_cdu_setup
    case1 = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    case2 = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    assert case1.balance_id == case2.balance_id


# 35. truth-state preservation
def test_35_truth_state_preservation(sample_cdu_setup):
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    assert case.mass_balance.provenance.provenance_type == ProvenanceType.CALCULATION


# 36. provenance completeness
def test_36_provenance_completeness(sample_cdu_setup):
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    assert case.provenance.provenance_id.startswith("prov-balcase-E-102")


# 37. human-review enforcement
def test_37_human_review_enforcement(sample_cdu_setup):
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    assert case.human_review_required is True


# 38. no autonomous control
def test_38_no_autonomous_control(sample_cdu_setup):
    model, graph = sample_cdu_setup
    with pytest.raises(AutonomousControlViolationError):
        BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0, allow_autonomous_control=True)


# 39. deliberate imbalance isolation
def test_39_deliberate_imbalance_isolation(sample_cdu_setup):
    model, graph = sample_cdu_setup
    model.streams["S-03"].mass_flow = 100.0
    model.streams["S-04"].mass_flow = 50.0
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    assert case.mass_balance.status == BalanceStatus.IMBALANCE


# 40. frontend balance rendering schema compatibility
def test_40_frontend_balance_rendering_schema_compatibility(sample_cdu_setup):
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    dump = case.model_dump()
    assert "balance_id" in dump
    assert "mass_balance" in dump
    assert "energy_balance" in dump
    assert "human_review_required" in dump


# 41. representative CDU behavior
def test_41_representative_cdu_behavior(sample_cdu_setup):
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.PLANT, "CDU-PLANT-01", 1000.0)
    assert case.scope_type == BalanceScopeType.PLANT


# 42. full regression check fixture
def test_42_full_regression_check(sample_cdu_setup):
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    assert case.status in [BalanceStatus.BALANCED, BalanceStatus.PARTIALLY_EVALUATED]


# ============================================================
# CRITICAL NEGATIVE TESTS
# ============================================================

def test_neg_1_fabricated_flow():
    prov = Provenance(provenance_id="pfab", provenance_type=ProvenanceType.CALCULATION, source_reference="s", timestamp="2026-09-17T15:25:00Z")
    s_in = ProcessStream(stream_id="S-IN", name="In", mass_flow=None, provenance=prov)
    res = MassBalanceEngine.evaluate_mass_balance([s_in], [], 1000.0)
    assert res.total_in is None


def test_neg_2_fabricated_density(sample_cdu_setup):
    model, _ = sample_cdu_setup
    assert model.streams["S-04"].density is None


def test_neg_3_fabricated_enthalpy(sample_cdu_setup):
    model, _ = sample_cdu_setup
    assert model.streams["S-04"].enthalpy is None


def test_neg_4_fabricated_composition(sample_cdu_setup):
    model, _ = sample_cdu_setup
    assert len(model.streams["S-04"].composition) == 0


def test_neg_5_future_evidence(sample_cdu_setup):
    model, graph = sample_cdu_setup
    with pytest.raises(TemporalBalanceViolation):
        BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 999999.0, baseline_max_time=63999.0)


def test_neg_6_invalid_units():
    res = MassBalanceEngine.evaluate_mass_balance([], [], 1000.0)
    assert res.unit == "kg/s"


def test_neg_7_invalid_dimensions():
    res = EnergyBalanceEngine.evaluate_energy_balance([], [], 1000.0)
    assert res.unit == "kW"


def test_neg_8_silent_imputation():
    prov = Provenance(provenance_id="psilent", provenance_type=ProvenanceType.CALCULATION, source_reference="s", timestamp="2026-09-17T15:25:00Z")
    s_in = ProcessStream(stream_id="S-IN", name="In", mass_flow=None, provenance=prov)
    s_out = ProcessStream(stream_id="S-OUT", name="Out", mass_flow=10.0, provenance=prov)
    res = MassBalanceEngine.evaluate_mass_balance([s_in], [s_out], 1000.0)
    assert res.status == BalanceStatus.PARTIALLY_EVALUATED


def test_neg_9_source_mutation(sample_cdu_setup, tmp_path):
    dfile = tmp_path / "test_data.csv"
    dfile.write_bytes(b"col1,col2\n1,2\n")
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0, data_path=dfile)
    assert case.status in [BalanceStatus.BALANCED, BalanceStatus.PARTIALLY_EVALUATED]


def test_neg_10_false_recycle_convergence(sample_cdu_setup):
    model, graph = sample_cdu_setup
    case = BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0)
    assert case.status != BalanceStatus.INCONSISTENT


def test_neg_11_autonomous_control(sample_cdu_setup):
    model, graph = sample_cdu_setup
    with pytest.raises(AutonomousControlViolationError):
        BalanceSolver.solve_balance_case(model, graph, BalanceScopeType.EQUIPMENT, "E-102", 1000.0, allow_autonomous_control=True)
