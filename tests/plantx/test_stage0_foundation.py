"""Stage-0 comprehensive unit test suite for PLANT-X foundation."""

import pytest
from pydantic import ValidationError
from src.plantx.domain import (
    Plant,
    Asset,
    Measurement,
    Stream,
    TruthState,
    Provenance,
    ProvenanceType,
    Geometry,
)
from src.plantx.validation.validator import PlantValidator, ValidationErrorType
from src.plantx.graph.plant_graph import PlantGraph, PlantEdgeType
from src.plantx.graph.evidence_graph import EvidenceGraph, EvidenceEdgeType
from src.plantx.contracts.safety import SafetyContract, OperationalAction, SafetyViolationError
from src.plantx.adapters.foulx_adapter import FoulXAdapter
from src.foulx.replay import ReplayService


def test_1_valid_plant():
    prov = Provenance(
        provenance_id="p-01",
        provenance_type=ProvenanceType.SENSOR,
        source_reference="TAG-101",
        timestamp="2026-09-17T00:00:00Z",
    )
    plant = Plant(plant_id="PL-01", name="Alpha", location="US", truth_state=TruthState.OBSERVED, provenance=prov)
    asset = Asset(asset_id="HX-01", plant_id="PL-01", name="Exchanger", asset_type="HX", truth_state=TruthState.OBSERVED, provenance=prov)
    stream = Stream(stream_id="ST-01", name="Crude", truth_state=TruthState.OBSERVED, provenance=prov)
    m = Measurement(
        measurement_id="M-01",
        sensor_id="S-01",
        stream_id="ST-01",
        parameter_name="Temp",
        value=350.0,
        unit="K",
        truth_state=TruthState.OBSERVED,
        provenance=prov,
    )

    errs = PlantValidator.validate_plant_topology(plant, [asset], [m], [stream])
    assert len(errs) == 0


def test_2_missing_asset_id():
    prov = Provenance(provenance_id="p-01", provenance_type=ProvenanceType.SENSOR, source_reference="TAG-101", timestamp="2026-09-17T00:00:00Z")
    plant = Plant(plant_id="PL-01", name="Alpha", location="US", truth_state=TruthState.OBSERVED)
    asset = Asset(asset_id="", plant_id="PL-01", name="Exchanger", asset_type="HX", truth_state=TruthState.OBSERVED)
    errs = PlantValidator.validate_plant_topology(plant, [asset], [], [])
    assert any(e.error_type == ValidationErrorType.MISSING_IDENTIFIER for e in errs)


def test_3_duplicate_asset():
    prov = Provenance(provenance_id="p-01", provenance_type=ProvenanceType.SENSOR, source_reference="TAG-101", timestamp="2026-09-17T00:00:00Z")
    plant = Plant(plant_id="PL-01", name="Alpha", location="US", truth_state=TruthState.OBSERVED)
    a1 = Asset(asset_id="HX-01", plant_id="PL-01", name="Exchanger 1", asset_type="HX", truth_state=TruthState.OBSERVED)
    a2 = Asset(asset_id="HX-01", plant_id="PL-01", name="Exchanger 2", asset_type="HX", truth_state=TruthState.OBSERVED)
    errs = PlantValidator.validate_plant_topology(plant, [a1, a2], [], [])
    assert any(e.error_type == ValidationErrorType.DUPLICATE_IDENTITY for e in errs)


def test_4_missing_unit():
    prov = Provenance(provenance_id="p-01", provenance_type=ProvenanceType.SENSOR, source_reference="TAG-101", timestamp="2026-09-17T00:00:00Z")
    plant = Plant(plant_id="PL-01", name="Alpha", location="US", truth_state=TruthState.OBSERVED)
    m = Measurement(measurement_id="M-01", sensor_id="S-01", stream_id="ST-01", parameter_name="Temp", value=100.0, unit="FOO", truth_state=TruthState.OBSERVED, provenance=prov)
    errs = PlantValidator.validate_plant_topology(plant, [], [m], [])
    assert any(e.error_type == ValidationErrorType.INVALID_UNIT for e in errs)


def test_5_invalid_measurement():
    prov = Provenance(provenance_id="p-01", provenance_type=ProvenanceType.SENSOR, source_reference="TAG-101", timestamp="2026-09-17T00:00:00Z")
    plant = Plant(plant_id="PL-01", name="Alpha", location="US", truth_state=TruthState.OBSERVED)
    m = Measurement(measurement_id="M-01", sensor_id="S-01", stream_id="ST-01", parameter_name="Temp", value=-10.0, unit="K", truth_state=TruthState.OBSERVED, provenance=prov)
    errs = PlantValidator.validate_plant_topology(plant, [], [m], [])
    assert any(e.error_type == ValidationErrorType.IMPOSSIBLE_VALUE for e in errs)


def test_6_missing_provenance():
    plant = Plant(plant_id="PL-01", name="Alpha", location="US", truth_state=TruthState.OBSERVED)
    m = Measurement(measurement_id="M-01", sensor_id="S-01", stream_id="ST-01", parameter_name="Temp", value=300.0, unit="K", truth_state=TruthState.OBSERVED, provenance=None)
    errs = PlantValidator.validate_plant_topology(plant, [], [m], [])
    assert any(e.error_type == ValidationErrorType.MISSING_PROVENANCE for e in errs)


def test_7_unresolved_equipment():
    a = Asset(asset_id="HX-UNRESOLVED", plant_id="PL-01", name="Unknown HX", asset_type="HX", truth_state=TruthState.UNRESOLVED)
    assert a.truth_state == TruthState.UNRESOLVED


def test_8_representative_geometry():
    g = Geometry(geometry_id="GEO-01", asset_id="HX-01", surface_area_m2=120.0, truth_state=TruthState.REPRESENTATIVE)
    assert g.truth_state == TruthState.REPRESENTATIVE


def test_9_observed_measurement():
    prov = Provenance(provenance_id="p-01", provenance_type=ProvenanceType.SENSOR, source_reference="TAG-101", timestamp="2026-09-17T00:00:00Z")
    m = Measurement(measurement_id="M-01", sensor_id="S-01", stream_id="ST-01", parameter_name="Flow", value=50.0, unit="kg/s", truth_state=TruthState.OBSERVED, provenance=prov)
    assert m.truth_state == TruthState.OBSERVED


def test_10_inferred_calculation():
    prov = Provenance(provenance_id="p-01", provenance_type=ProvenanceType.CALCULATION, source_reference="M2_Physics", timestamp="2026-09-17T00:00:00Z")
    m = Measurement(measurement_id="M-01", sensor_id="CALC-RF", stream_id="ST-01", parameter_name="Rf", value=0.0004, unit="m2K/W", truth_state=TruthState.INFERRED, provenance=prov)
    assert m.truth_state == TruthState.INFERRED


def test_11_contradictory_evidence():
    prov = Provenance(provenance_id="p-01", provenance_type=ProvenanceType.CALCULATION, source_reference="M2_Physics", timestamp="2026-09-17T00:00:00Z")
    plant = Plant(plant_id="PL-01", name="Alpha", location="US", truth_state=TruthState.OBSERVED)
    m = Measurement(measurement_id="M-01", sensor_id="CALC-RF", stream_id="ST-01", parameter_name="Rf", value=0.0004, unit="m2K/W", truth_state=TruthState.OBSERVED, provenance=prov)
    errs = PlantValidator.validate_plant_topology(plant, [], [m], [])
    assert any(e.error_type == ValidationErrorType.CONTRADICTORY_TRUTH_STATE for e in errs)


def test_12_orphan_measurement():
    prov = Provenance(provenance_id="p-01", provenance_type=ProvenanceType.SENSOR, source_reference="TAG-101", timestamp="2026-09-17T00:00:00Z")
    plant = Plant(plant_id="PL-01", name="Alpha", location="US", truth_state=TruthState.OBSERVED)
    m = Measurement(measurement_id="M-01", sensor_id="S-01", stream_id="NON_EXISTENT_STREAM", parameter_name="Temp", value=300.0, unit="K", truth_state=TruthState.OBSERVED, provenance=prov)
    errs = PlantValidator.validate_plant_topology(plant, [], [m], [])
    assert any(e.error_type == ValidationErrorType.ORPHAN_MEASUREMENT for e in errs)


def test_13_invalid_graph_relationship():
    pg = PlantGraph()
    pg.add_node("A1", "Asset")
    with pytest.raises(ValueError):
        pg.add_edge("A1", "MISSING_NODE", PlantEdgeType.CONNECTED_TO)


def test_14_deterministic_serialization():
    prov = Provenance(provenance_id="p-01", provenance_type=ProvenanceType.SENSOR, source_reference="TAG-101", timestamp="2026-09-17T00:00:00Z")
    plant1 = Plant(plant_id="PL-01", name="Alpha", location="US", truth_state=TruthState.OBSERVED, provenance=prov)
    plant2 = Plant(plant_id="PL-01", name="Alpha", location="US", truth_state=TruthState.OBSERVED, provenance=prov)
    assert plant1.model_dump_json() == plant2.model_dump_json()


def test_15_schema_version_compatibility():
    plant = Plant(plant_id="PL-01", name="Alpha", location="US", truth_state=TruthState.OBSERVED)
    assert plant.version == "1.0.0"


def test_16_safety_contract():
    action = OperationalAction(action_type="SHUTDOWN", target_equipment="HX-101", command_payload={}, human_approved=False)
    with pytest.raises(SafetyViolationError):
        SafetyContract.validate_action(action)


from pathlib import Path
def test_17_foulx_compatibility():
    service = ReplayService(data_path=Path("data/raw/heat_exchanger_fouling_dataset.csv"))
    snapshot = service.get_snapshot(50.0)
    domain_dict = FoulXAdapter.to_plantx_domain(snapshot)
    assert domain_dict["plant"].plant_id == "PLANT-01"
    assert domain_dict["asset"].asset_id == "HX-101"
    assert len(domain_dict["measurements"]) == 3
    assert domain_dict["decision"] is not None
