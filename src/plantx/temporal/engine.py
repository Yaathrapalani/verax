"""Temporal processing engine enforcing zero-leakage causal temporal integrity."""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.temporal.schemas import (
    TemporalObservation,
    TemporalStatus,
    SamplingClassification,
    MissingnessReason,
    FreshnessStatus,
    FreshnessPolicy,
    ImputationPolicy,
    TemporalEvidenceState,
    OverallTemporalUsability,
)


class CausalTemporalLeakageError(Exception):
    """Raised when an illegal future observation is accessed during temporal alignment."""
    pass


class TemporalEvidenceEngine:
    """Core engine processing observations into deterministic TemporalEvidenceState."""

    @classmethod
    def validate_timestamp_sequence(cls, observations: List[TemporalObservation]) -> Tuple[TemporalStatus, List[str]]:
        reasons = []
        if not observations:
            return TemporalStatus.VALID, reasons

        # Group by measurement_id
        by_channel: Dict[str, List[float]] = {}
        for o in observations:
            by_channel.setdefault(o.measurement_id, []).append(o.observed_at)

        for channel, ts_list in by_channel.items():
            if len(ts_list) != len(set(ts_list)):
                reasons.append(f"Duplicate timestamps detected in channel {channel}")
                return TemporalStatus.DUPLICATE_TIMESTAMP, reasons

        return TemporalStatus.VALID, reasons

    @classmethod
    def characterize_sampling(cls, timestamps: List[float]) -> SamplingClassification:
        if len(timestamps) < 3:
            return SamplingClassification.INSUFFICIENT_HISTORY

        deltas = np.diff(timestamps)
        std_delta = np.std(deltas)
        mean_delta = np.mean(deltas)

        if mean_delta <= 0:
            return SamplingClassification.UNKNOWN

        cv = std_delta / mean_delta
        if cv < 0.1:
            return SamplingClassification.REGULAR
        elif cv > 1.5:
            return SamplingClassification.BURSTY
        else:
            return SamplingClassification.IRREGULAR

    @classmethod
    def align_causally(
        cls,
        observations: List[TemporalObservation],
        target_time: float,
        strict_causal: bool = False,
    ) -> List[TemporalObservation]:
        """Filters observations where observed_at <= target_time to prevent future data leakage."""
        aligned = []
        for obs in observations:
            if obs.observed_at > target_time:
                if strict_causal:
                    raise CausalTemporalLeakageError(
                        f"CRITICAL CAUSAL LEAKAGE: Observation {obs.observation_id} at t={obs.observed_at} "
                        f"exceeds target evaluation time T={target_time}."
                    )
                continue
            aligned.append(obs)
        return aligned

    @classmethod
    def evaluate_freshness(
        cls,
        aligned_obs: List[TemporalObservation],
        target_time: float,
        policy: Optional[FreshnessPolicy] = None,
    ) -> Dict[str, FreshnessStatus]:
        freshness_map = {}
        for obs in aligned_obs:
            age = target_time - obs.observed_at
            obs.observation_age = age
            if policy and obs.measurement_id in policy.max_acceptable_age_hours:
                max_age = policy.max_acceptable_age_hours[obs.measurement_id]
                freshness_map[obs.measurement_id] = FreshnessStatus.FRESH if age <= max_age else FreshnessStatus.STALE
            else:
                freshness_map[obs.measurement_id] = FreshnessStatus.FRESHNESS_UNSPECIFIED
        return freshness_map

    @classmethod
    def build_temporal_evidence_state(
        cls,
        observations: List[TemporalObservation],
        target_time: float,
        freshness_policy: Optional[FreshnessPolicy] = None,
        imputation_policy: Optional[ImputationPolicy] = None,
    ) -> TemporalEvidenceState:
        prov = Provenance(
            provenance_id=f"prov-temporal-{int(target_time)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="TemporalEvidenceEngine",
            timestamp="2026-09-17T12:28:00Z",
            transformation_applied="Causal Alignment + Freshness + Usability Evaluation",
        )

        # 1. Causal alignment
        aligned = cls.align_causally(observations, target_time, strict_causal=False)

        # 2. Timestamp validation
        ts_status, ts_reasons = cls.validate_timestamp_sequence(aligned)
        ts_list = [o.observed_at for o in aligned]

        # 3. Sampling classification
        sampling_class = cls.characterize_sampling(ts_list)

        # 4. Freshness evaluation
        freshness = cls.evaluate_freshness(aligned, target_time, freshness_policy)

        # 5. Usability state derivation
        has_stale = any(status == FreshnessStatus.STALE for status in freshness.values())
        has_missing = any(o.value is None and not o.is_imputed for o in aligned)

        if ts_status != TemporalStatus.VALID:
            usability = OverallTemporalUsability.UNAVAILABLE
        elif has_stale or has_missing or sampling_class in {SamplingClassification.INSUFFICIENT_HISTORY, SamplingClassification.IRREGULAR, SamplingClassification.BURSTY}:
            usability = OverallTemporalUsability.CONDITIONALLY_USABLE
        else:
            usability = OverallTemporalUsability.USABLE

        return TemporalEvidenceState(
            target_time=target_time,
            timestamp_integrity=ts_status.value,
            completeness_fraction=sum(1 for o in aligned if o.value is not None) / max(len(aligned), 1),
            freshness_summary=freshness,
            sampling_classification=sampling_class,
            history_depth_hours=(max(ts_list) - min(ts_list)) if len(ts_list) > 1 else 0.0,
            imputation_fraction=sum(1 for o in aligned if o.is_imputed) / max(len(aligned), 1),
            usability=usability,
            provenance=prov,
        )
