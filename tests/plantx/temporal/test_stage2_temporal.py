"""Comprehensive Stage-2 Temporal Evidence Test Suite."""

import pytest
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.temporal import (
    TemporalObservation,
    TemporalEvidenceEngine,
    FreshnessPolicy,
    FreshnessStatus,
    ImputationPolicy,
    SamplingClassification,
    OverallTemporalUsability,
    CausalTemporalLeakageError,
)


@pytest.fixture
def base_prov():
    return Provenance(
        provenance_id="p-temp-test",
        provenance_type=ProvenanceType.SENSOR,
        source_reference="TAG-101",
        timestamp="2026-09-17T12:00:00Z",
    )


def test_1_regular_complete_data(base_prov):
    obs = [
        TemporalObservation(observation_id=f"o-{i}", source_id="s1", asset_id="HX-101", measurement_id="TI-101", observed_at=float(i), value=300.0 + i, provenance=base_prov)
        for i in range(10)
    ]
    state = TemporalEvidenceEngine.build_temporal_evidence_state(obs, target_time=9.0)
    assert state.usability == OverallTemporalUsability.USABLE
    assert state.sampling_classification == SamplingClassification.REGULAR


def test_2_random_missing_observations(base_prov):
    obs = [
        TemporalObservation(observation_id=f"o-{i}", source_id="s1", asset_id="HX-101", measurement_id="TI-101", observed_at=float(i), value=300.0 if i % 2 == 0 else None, provenance=base_prov)
        for i in range(10)
    ]
    state = TemporalEvidenceEngine.build_temporal_evidence_state(obs, target_time=9.0)
    assert state.usability == OverallTemporalUsability.CONDITIONALLY_USABLE
    assert state.completeness_fraction == 0.5


def test_3_long_missing_block(base_prov):
    obs = [
        TemporalObservation(observation_id=f"o-{i}", source_id="s1", asset_id="HX-101", measurement_id="TI-101", observed_at=float(i), value=300.0 if i < 2 else None, provenance=base_prov)
        for i in range(10)
    ]
    state = TemporalEvidenceEngine.build_temporal_evidence_state(obs, target_time=9.0)
    assert state.usability == OverallTemporalUsability.CONDITIONALLY_USABLE


def test_4_asynchronous_sampling(base_prov):
    obs_temp = [TemporalObservation(observation_id=f"ot-{i}", source_id="s1", asset_id="HX-101", measurement_id="TI-101", observed_at=float(i), value=300.0, provenance=base_prov) for i in range(10)]
    obs_lab = [TemporalObservation(observation_id=f"ol-{i}", source_id="s2", asset_id="HX-101", measurement_id="LAB-01", observed_at=float(i * 5), value=0.0004, provenance=base_prov) for i in range(2)]
    state = TemporalEvidenceEngine.build_temporal_evidence_state(obs_temp + obs_lab, target_time=5.0)
    assert state.usability in {OverallTemporalUsability.USABLE, OverallTemporalUsability.CONDITIONALLY_USABLE}


def test_5_irregular_sampling(base_prov):
    ts = [0.0, 1.0, 4.0, 5.0, 11.0, 12.0]
    obs = [TemporalObservation(observation_id=f"o-{i}", source_id="s1", asset_id="HX-101", measurement_id="TI-101", observed_at=t, value=300.0, provenance=base_prov) for i, t in enumerate(ts)]
    state = TemporalEvidenceEngine.build_temporal_evidence_state(obs, target_time=12.0)
    assert state.sampling_classification in {SamplingClassification.IRREGULAR, SamplingClassification.BURSTY}


def test_6_stale_evidence(base_prov):
    obs = [TemporalObservation(observation_id="o-1", source_id="s1", asset_id="HX-101", measurement_id="TI-101", observed_at=0.0, value=300.0, provenance=base_prov)]
    policy = FreshnessPolicy(max_acceptable_age_hours={"TI-101": 2.0})
    state = TemporalEvidenceEngine.build_temporal_evidence_state(obs, target_time=10.0, freshness_policy=policy)
    assert state.freshness_summary["TI-101"] == FreshnessStatus.STALE
    assert state.usability == OverallTemporalUsability.CONDITIONALLY_USABLE


def test_7_future_leakage_attack(base_prov):
    obs = [
        TemporalObservation(observation_id="o-past", source_id="s1", asset_id="HX-101", measurement_id="TI-101", observed_at=5.0, value=300.0, provenance=base_prov),
        TemporalObservation(observation_id="o-future", source_id="s1", asset_id="HX-101", measurement_id="TI-101", observed_at=15.0, value=999.0, provenance=base_prov),
    ]
    with pytest.raises(CausalTemporalLeakageError):
        TemporalEvidenceEngine.align_causally(obs, target_time=10.0, strict_causal=True)


def test_8_permitted_imputation(base_prov):
    obs = TemporalObservation(observation_id="o-imp", source_id="s1", asset_id="HX-101", measurement_id="TI-101", observed_at=5.0, value=300.0, is_imputed=True, imputation_method="FORWARD_FILL", provenance=base_prov)
    assert obs.is_imputed is True
    assert obs.imputation_method == "FORWARD_FILL"


def test_9_forbidden_imputation(base_prov):
    obs = TemporalObservation(observation_id="o-raw", source_id="s1", asset_id="HX-101", measurement_id="TI-101", observed_at=5.0, value=None, is_imputed=False, provenance=base_prov)
    assert obs.value is None
    assert obs.is_imputed is False


def test_10_deterministic_execution(base_prov):
    obs = [TemporalObservation(observation_id=f"o-{i}", source_id="s1", asset_id="HX-101", measurement_id="TI-101", observed_at=float(i), value=300.0, provenance=base_prov) for i in range(5)]
    s1 = TemporalEvidenceEngine.build_temporal_evidence_state(obs, target_time=4.0)
    s2 = TemporalEvidenceEngine.build_temporal_evidence_state(obs, target_time=4.0)
    assert s1.model_dump_json() == s2.model_dump_json()
