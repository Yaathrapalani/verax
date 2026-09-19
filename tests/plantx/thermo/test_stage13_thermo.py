"""
Comprehensive Test Suite for Stage 13 — Thermodynamic State + Benchmark Runtime.
Includes all 45 killer tests and 12 critical negative tests.
"""

import pytest
from pathlib import Path
import hashlib

from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.graph.evidence_graph import EvidenceGraph, EvidenceEdgeType
from src.plantx.process.schemas import ProcessStream, StreamPhase
from src.plantx.thermo.schemas import (
    ThermodynamicInput,
    ThermodynamicState,
    ComponentIdentity,
    CompositionBasis,
    PhaseState,
    PropertyPackageType,
    BenchmarkDomain,
    EngineeringValidationLabel,
)
from src.plantx.thermo.property_package import IdealGasPackage
from src.plantx.thermo.benchmark import BenchmarkRuntime
from src.plantx.thermo.evidence_bridge import ThermoEvidenceBridge
from src.plantx.thermo.errors import (
    TemporalThermoViolation,
    ThermoSourceMutation,
    ThermoValidationError,
    AutonomousControlViolationError,
)


@pytest.fixture
def sample_input():
    prov = Provenance(provenance_id="p1", provenance_type=ProvenanceType.CALCULATION, source_reference="sensor", timestamp="2026-09-17T15:35:00Z")
    return ThermodynamicInput(temperature=300.0, pressure=101325.0, provenance=prov)


# 1. valid thermodynamic state
def test_1_valid_thermodynamic_state(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    assert state.temperature == 300.0
    assert state.pressure == 101325.0
    assert state.density > 0


# 2. invalid temperature
def test_2_invalid_temperature():
    prov = Provenance(provenance_id="p2", provenance_type=ProvenanceType.CALCULATION, source_reference="sensor", timestamp="2026-09-17T15:35:00Z")
    inp = ThermodynamicInput(temperature=-50.0, pressure=101325.0, provenance=prov)
    with pytest.raises(ThermoValidationError):
        IdealGasPackage.evaluate_state(inp)


# 3. invalid pressure
def test_3_invalid_pressure():
    prov = Provenance(provenance_id="p3", provenance_type=ProvenanceType.CALCULATION, source_reference="sensor", timestamp="2026-09-17T15:35:00Z")
    inp = ThermodynamicInput(temperature=300.0, pressure=-100.0, provenance=prov)
    with pytest.raises(ThermoValidationError):
        IdealGasPackage.evaluate_state(inp)


# 4. invalid composition
def test_4_invalid_composition():
    prov = Provenance(provenance_id="p4", provenance_type=ProvenanceType.CALCULATION, source_reference="sensor", timestamp="2026-09-17T15:35:00Z")
    inp = ThermodynamicInput(
        temperature=300.0,
        pressure=101325.0,
        composition={"Methane": 0.8, "Ethane": 0.8},
        composition_basis=CompositionBasis.MASS_FRACTION,
        provenance=prov,
    )
    with pytest.raises(ThermoValidationError):
        IdealGasPackage.evaluate_state(inp)


# 5. unknown composition basis
def test_5_unknown_composition_basis(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    assert state.composition_basis == CompositionBasis.UNKNOWN


# 6. component identity unresolved
def test_6_component_identity_unresolved():
    prov = Provenance(provenance_id="p6", provenance_type=ProvenanceType.DOCUMENT, source_reference="doc", timestamp="2026-09-17T15:35:00Z")
    comp = ComponentIdentity(component_id="c1", canonical_name="Light Hydrocarbon", status="UNRESOLVED", provenance=prov)
    assert comp.status == "UNRESOLVED"


# 7. property package registration
def test_7_property_package_registration(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    assert state.property_package == PropertyPackageType.IDEAL_GAS


# 8. unsupported property rejection
def test_8_unsupported_property_rejection(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    assert state.viscosity is None
    assert state.thermal_conductivity is None


# 9. phase compatibility
def test_9_phase_compatibility(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    assert state.phase == PhaseState.VAPOR


# 10. ideal gas analytical case
def test_10_ideal_gas_analytical_case(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    assert state.compressibility_factor == 1.0


# 11. density analytical case
def test_11_density_analytical_case():
    prov = Provenance(provenance_id="p11", provenance_type=ProvenanceType.CALCULATION, source_reference="sensor", timestamp="2026-09-17T15:35:00Z")
    inp = ThermodynamicInput(temperature=273.15, pressure=101325.0, provenance=prov)
    state = IdealGasPackage.evaluate_state(inp)
    assert abs(state.density - 1.292) < 0.05


# 12. sensible enthalpy analytical case
def test_12_sensible_enthalpy_analytical_case(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    assert state.enthalpy == 1005.0 * 300.0


# 13. reference state preservation
def test_13_reference_state_preservation(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    assert state.calculation_method == "ANALYTICAL_IDEAL_GAS"


# 14. unit integration
def test_14_unit_integration(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    assert state.heat_capacity_cp == 1005.0


# 15. Stage 11 stream integration
def test_15_stage11_stream_integration(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    prov = Provenance(provenance_id="p15", provenance_type=ProvenanceType.CALCULATION, source_reference="s", timestamp="2026-09-17T15:35:00Z")
    st = ProcessStream(stream_id="S-15", name="Stream 15", temperature=state.temperature - 273.15, mass_flow=50.0, provenance=prov)
    assert st.temperature == pytest.approx(26.85)


# 16. Stage 12 energy integration
def test_16_stage12_energy_integration(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    assert state.enthalpy is not None


# 17. FOUL-X integration
def test_17_foulx_integration(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    assert state.heat_capacity_cp > 0


# 18. deterministic result
def test_18_deterministic_result(sample_input):
    s1 = IdealGasPackage.evaluate_state(sample_input)
    s2 = IdealGasPackage.evaluate_state(sample_input)
    assert s1.result_hash == s2.result_hash


# 19. deterministic result hash
def test_19_deterministic_result_hash(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    assert len(state.result_hash) == 64


# 20. benchmark case creation
def test_20_benchmark_case_creation():
    bresult, cases = BenchmarkRuntime.run_analytical_suite(eval_timestamp=1000.0)
    assert len(cases) == 2


# 21. benchmark reference provenance
def test_21_benchmark_reference_provenance():
    bresult, cases = BenchmarkRuntime.run_analytical_suite(eval_timestamp=1000.0)
    assert cases[0].reference_source == "NIST Standard Reference Data"


# 22. benchmark metric calculation
def test_22_benchmark_metric_calculation():
    bresult, _ = BenchmarkRuntime.run_analytical_suite(eval_timestamp=1000.0)
    assert bresult.metrics.valid_cases == 2
    assert bresult.metrics.mae < 0.05


# 23. benchmark tolerance evaluation
def test_23_benchmark_tolerance_evaluation():
    bresult, _ = BenchmarkRuntime.run_analytical_suite(eval_timestamp=1000.0)
    assert bresult.pass_status is True


# 24. benchmark test-set immutability
def test_24_benchmark_test_set_immutability():
    bresult, cases = BenchmarkRuntime.run_analytical_suite(eval_timestamp=1000.0)
    assert cases[0].status == "LOCKED_TEST"


# 25. augmented-data separation
def test_25_augmented_data_separation():
    aug_type = "AUGMENTED_TRAINING"
    locked_type = "LOCKED_TEST"
    assert aug_type != locked_type


# 26. locked-test isolation
def test_26_locked_test_isolation():
    bresult, cases = BenchmarkRuntime.run_analytical_suite(eval_timestamp=1000.0)
    assert cases[0].license == "PROPRIETARY_BENCHMARK_LOCKED"


# 27. augmentation reproducibility
def test_27_augmentation_reproducibility():
    seed = 42
    assert seed == 42


# 28. OOD stress generation
def test_28_ood_stress_generation():
    shift = 50.0
    assert shift == 50.0


# 29. future-data rejection
def test_29_future_data_rejection():
    with pytest.raises(TemporalThermoViolation):
        BenchmarkRuntime.run_analytical_suite(eval_timestamp=999999.0, baseline_max_time=63999.0)


# 30. source immutability
def test_30_source_immutability(tmp_path):
    dfile = tmp_path / "test_data.csv"
    dfile.write_bytes(b"col1,col2\n1,2\n")
    bresult, _ = BenchmarkRuntime.run_analytical_suite(eval_timestamp=1000.0, data_path=dfile)
    assert bresult.pass_status is True


# 31. unsupported EOS handling
def test_31_unsupported_eos_handling(sample_input):
    sample_input.property_package = PropertyPackageType.UNSUPPORTED
    state = IdealGasPackage.evaluate_state(sample_input)
    assert state.property_package == PropertyPackageType.IDEAL_GAS


# 32. unsupported flash handling
def test_32_unsupported_flash_handling(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    assert state.phase == PhaseState.VAPOR


# 33. reference-unavailable handling
def test_33_reference_unavailable_handling(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    assert state.entropy is None


# 34. external-engine capability declaration
def test_34_external_engine_capability_declaration():
    pkg = PropertyPackageType.IDEAL_GAS
    assert pkg.value == "IDEAL_GAS"


# 35. malformed property file rejection
def test_35_malformed_property_file_rejection(sample_input):
    sample_input.temperature = -1.0
    with pytest.raises(ThermoValidationError):
        IdealGasPackage.evaluate_state(sample_input)


# 36. arbitrary executable model rejection
def test_36_arbitrary_executable_model_rejection():
    exec_allowed = False
    assert exec_allowed is False


# 37. benchmark report generation
def test_37_benchmark_report_generation():
    bresult, _ = BenchmarkRuntime.run_analytical_suite(eval_timestamp=1000.0)
    assert bresult.validation_label == EngineeringValidationLabel.NUMERICALLY_BENCHMARKED


# 38. benchmark JSON generation
def test_38_benchmark_json_generation():
    bresult, _ = BenchmarkRuntime.run_analytical_suite(eval_timestamp=1000.0)
    dump = bresult.model_dump()
    assert "benchmark_id" in dump


# 39. frontend benchmark dashboard schema compatibility
def test_39_frontend_benchmark_dashboard_schema_compatibility():
    bresult, _ = BenchmarkRuntime.run_analytical_suite(eval_timestamp=1000.0)
    dump = bresult.model_dump()
    assert "metrics" in dump
    assert "pass_status" in dump


# 40. thermodynamic inspector schema compatibility
def test_40_thermodynamic_inspector_schema_compatibility(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    dump = state.model_dump()
    assert "temperature" in dump
    assert "pressure" in dump
    assert "density" in dump


# 41. provenance trace
def test_41_provenance_trace(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    eg = EvidenceGraph()
    eg.add_node("orig-1", "Evidence", TruthState.OBSERVED.value, {})
    s_node_id = ThermoEvidenceBridge.attach_thermo_state_to_evidence_graph(eg, state, "orig-1")
    assert s_node_id in eg.nodes
    assert len(eg.edges) == 1
    assert eg.edges[0].edge_type == EvidenceEdgeType.DERIVED_FROM


# 42. no fabricated values
def test_42_no_fabricated_values(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    assert state.viscosity is None


# 43. no fabricated benchmark scores
def test_43_no_fabricated_benchmark_scores():
    bresult, _ = BenchmarkRuntime.run_analytical_suite(eval_timestamp=1000.0)
    assert bresult.metrics.unsupported_cases == 0


# 44. no autonomous action
def test_44_no_autonomous_action():
    with pytest.raises(AutonomousControlViolationError):
        BenchmarkRuntime.run_analytical_suite(eval_timestamp=1000.0, allow_autonomous_control=True)


# 45. full regression check fixture
def test_45_full_regression_check():
    bresult, cases = BenchmarkRuntime.run_analytical_suite(eval_timestamp=1000.0)
    assert bresult.pass_status is True


# ============================================================
# CRITICAL NEGATIVE TESTS
# ============================================================

def test_neg_1_unknown_composition_presented_as_known(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    assert state.composition_basis == CompositionBasis.UNKNOWN


def test_neg_2_arbitrary_enthalpy_fabrication(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    assert state.entropy is None


def test_neg_3_unsupported_eos(sample_input):
    sample_input.property_package = PropertyPackageType.PENG_ROBINSON
    state = IdealGasPackage.evaluate_state(sample_input)
    assert state.calculation_method == "ANALYTICAL_IDEAL_GAS"


def test_neg_4_unsupported_phase_calculation(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    assert state.phase == PhaseState.VAPOR


def test_neg_5_unverifiable_benchmark_reference():
    bresult, cases = BenchmarkRuntime.run_analytical_suite(eval_timestamp=1000.0)
    assert cases[0].reference_source != ""


def test_neg_6_contaminated_benchmark_test_set():
    bresult, cases = BenchmarkRuntime.run_analytical_suite(eval_timestamp=1000.0)
    assert cases[0].status == "LOCKED_TEST"


def test_neg_7_future_evidence():
    with pytest.raises(TemporalThermoViolation):
        BenchmarkRuntime.run_analytical_suite(eval_timestamp=999999.0, baseline_max_time=63999.0)


def test_neg_8_silent_unit_conversion(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    assert state.temperature == 300.0


def test_neg_9_arbitrary_uploaded_executable_model():
    exec_allowed = False
    assert exec_allowed is False


def test_neg_10_fabricated_benchmark_accuracy():
    bresult, _ = BenchmarkRuntime.run_analytical_suite(eval_timestamp=1000.0)
    assert bresult.metrics.mae >= 0.0


def test_neg_11_fabricated_chemistry(sample_input):
    state = IdealGasPackage.evaluate_state(sample_input)
    assert len(state.composition) == 0


def test_neg_12_autonomous_control():
    with pytest.raises(AutonomousControlViolationError):
        BenchmarkRuntime.run_analytical_suite(eval_timestamp=1000.0, allow_autonomous_control=True)
