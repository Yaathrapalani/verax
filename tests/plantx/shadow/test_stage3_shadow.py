"""Comprehensive Stage-3 Digital Shadow Test Suite."""

import pytest
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.domain.entities import Asset
from src.plantx.intake.manifest import EvidenceManifest, ManifestStatus
from src.plantx.intake.parsers import ExtractionBundle
from src.plantx.intake.resolver import ResolutionStatus
from src.plantx.temporal.schemas import TemporalObservation
from src.plantx.temporal.engine import CausalTemporalLeakageError
from src.plantx.shadow import (
    DigitalShadowReconstructor,
    DigitalShadowSnapshot,
    AssetState,
)


@pytest.fixture
def base_prov():
    return Provenance(
        provenance_id="p-shadow-test",
        provenance_type=ProvenanceType.DOCUMENT,
        source_reference="DATASHEET-101.PDF",
        timestamp="2026-09-17T12:54:00Z",
    )


@pytest.fixture
def sample_bundle(base_prov):
    manifest = EvidenceManifest(
        source_id="src-doc-1",
        filename="DATASHEET-101.PDF",
        source_type="Engineering",
        format="pdf",
        size_bytes=1024,
        checksum_sha256="dummyhash",
        ingested_at="2026-09-17T12:54:00Z",
        parser_name="EngineeringDocumentParser",
        status=ManifestStatus.PARSED,
        provenance=base_prov,
    )
    asset = Asset(
        asset_id="E-101",
        plant_id="PLANT-01",
        name="Exchanger E-101",
        asset_type="HEAT_EXCHANGER",
        truth_state=TruthState.OBSERVED,
        provenance=base_prov,
    )
    return ExtractionBundle(manifest=manifest, extracted_assets=[asset])


@pytest.fixture
def sample_observations(base_prov):
    return [
        TemporalObservation(
            observation_id="obs-1",
            source_id="src-hist-1",
            asset_id="HX-101",
            measurement_id="TI-101",
            observed_at=10.0,
            value=350.0,
            provenance=base_prov,
        ),
        TemporalObservation(
            observation_id="obs-2",
            source_id="src-hist-1",
            asset_id="HX-101",
            measurement_id="TI-102",
            observed_at=10.0,
            value=300.0,
            provenance=base_prov,
        ),
    ]


def test_1_canonical_snapshot_construction(sample_bundle, sample_observations):
    reconstructor = DigitalShadowReconstructor()
    snapshot = reconstructor.reconstruct_snapshot(
        target_time=10.0,
        bundles=[sample_bundle],
        temporal_observations=sample_observations,
    )
    assert snapshot.plant_id == "PLANT-01"
    assert snapshot.target_time == 10.0
    assert "HX-101" in snapshot.asset_shadows


def test_2_asset_state_reconstruction(sample_bundle, sample_observations):
    reconstructor = DigitalShadowReconstructor()
    snapshot = reconstructor.reconstruct_snapshot(
        target_time=10.0,
        bundles=[sample_bundle],
        temporal_observations=sample_observations,
    )
    asset_st = snapshot.asset_shadows["HX-101"]
    assert asset_st.resolution_status == ResolutionStatus.RESOLVED
    assert len(asset_st.measurement_bindings) == 2


def test_3_truth_state_preservation(sample_bundle, sample_observations):
    reconstructor = DigitalShadowReconstructor()
    snapshot = reconstructor.reconstruct_snapshot(
        target_time=10.0,
        bundles=[sample_bundle],
        temporal_observations=sample_observations,
    )
    asset_st = snapshot.asset_shadows["HX-101"]
    assert asset_st.truth_state == TruthState.OBSERVED
    assert asset_st.geometry_state.truth_state == TruthState.REPRESENTATIVE


def test_4_future_data_rejection(sample_bundle, base_prov):
    obs_future = [
        TemporalObservation(
            observation_id="obs-future",
            source_id="src-1",
            asset_id="HX-101",
            measurement_id="TI-101",
            observed_at=20.0,
            value=999.0,
            provenance=base_prov,
        )
    ]
    reconstructor = DigitalShadowReconstructor()
    with pytest.raises(CausalTemporalLeakageError):
        reconstructor.reconstruct_snapshot(
            target_time=10.0,
            bundles=[sample_bundle],
            temporal_observations=obs_future,
            strict_causal=True,
        )


def test_5_deterministic_serialization(sample_bundle, sample_observations):
    reconstructor = DigitalShadowReconstructor()
    s1 = reconstructor.reconstruct_snapshot(10.0, [sample_bundle], sample_observations)
    s2 = reconstructor.reconstruct_snapshot(10.0, [sample_bundle], sample_observations)
    assert s1.provenance.deterministic_hash == s2.provenance.deterministic_hash


def test_6_unresolved_equipment_handling(base_prov):
    manifest = EvidenceManifest(
        source_id="src-doc-bad",
        filename="BAD.PDF",
        source_type="Engineering",
        format="pdf",
        size_bytes=100,
        checksum_sha256="badhash",
        ingested_at="2026-09-17T12:54:00Z",
        parser_name="EngineeringDocumentParser",
        status=ManifestStatus.PARSED,
        provenance=base_prov,
    )
    unresolved_asset = Asset(
        asset_id="E-999",
        plant_id="PLANT-01",
        name="Tag E-999",
        asset_type="UNRESOLVED",
        truth_state=TruthState.UNRESOLVED,
        provenance=base_prov,
    )
    bundle = ExtractionBundle(manifest=manifest, extracted_assets=[unresolved_asset])
    reconstructor = DigitalShadowReconstructor()
    snapshot = reconstructor.reconstruct_snapshot(10.0, [bundle], [])
    asset_st = snapshot.asset_shadows["E-999"]
    assert asset_st.resolution_status == ResolutionStatus.UNRESOLVED
    assert asset_st.truth_state == TruthState.UNRESOLVED
