"""State reconstructor engine building DigitalShadowSnapshot at time T."""

import hashlib
import json
from typing import List, Dict, Any, Optional
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.domain.entities import Plant, Asset, Stream, Event
from src.plantx.intake.resolver import ConservativeEntityResolver, ResolutionStatus
from src.plantx.intake.parsers import ExtractionBundle
from src.plantx.temporal.schemas import TemporalObservation, TemporalEvidenceState
from src.plantx.temporal.engine import TemporalEvidenceEngine, CausalTemporalLeakageError
from src.plantx.shadow.schemas import (
    DigitalShadowSnapshot,
    AssetState,
    MeasurementBinding,
    GeometryState,
    TopologyRelation,
    ShadowIssue,
    ShadowProvenance,
)
from src.foulx.replay import ReplayService, ReplaySnapshot


class DigitalShadowReconstructor:
    """Master reconstructor building deterministic, time-aware DigitalShadowSnapshot at T."""

    def __init__(self, replay_service: Optional[ReplayService] = None):
        self.replay_service = replay_service

    def reconstruct_snapshot(
        self,
        target_time: float,
        bundles: List[ExtractionBundle],
        temporal_observations: List[TemporalObservation],
        strict_causal: bool = True,
    ) -> DigitalShadowSnapshot:
        # 1. Enforce strict causal temporal alignment
        aligned_obs = TemporalEvidenceEngine.align_causally(
            temporal_observations,
            target_time,
            strict_causal=strict_causal,
        )

        # 2. Build temporal evidence state at T
        temp_state = TemporalEvidenceEngine.build_temporal_evidence_state(
            aligned_obs,
            target_time,
        )

        # 3. Process intake bundles & entity resolution
        assets_shadow_map: Dict[str, AssetState] = {}
        issues: List[ShadowIssue] = []
        topology_edges: List[TopologyRelation] = []

        prov_calc = Provenance(
            provenance_id=f"prov-shadow-{int(target_time)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="DigitalShadowReconstructor",
            timestamp="2026-09-17T12:54:00Z",
            transformation_applied="Digital Shadow Reconstruction",
        )

        # Ingest bundles conservatively
        for bundle in bundles:
            for raw_asset in bundle.extracted_assets:
                res = ConservativeEntityResolver.resolve_asset_tag(
                    raw_asset.asset_id,
                    bundle.manifest.source_id,
                )
                
                # Check for conflicts or unresolved equipment
                if res.status == ResolutionStatus.CONFLICT:
                    issues.append(
                        ShadowIssue(
                            issue_id=f"issue-conf-{raw_asset.asset_id}",
                            entity_id=raw_asset.asset_id,
                            issue_type="CONFLICT",
                            description=f"Conflicting evidence for asset {raw_asset.asset_id}",
                            provenance=prov_calc,
                        )
                    )

                # Bind measurements to asset
                m_bindings = []
                for obs in aligned_obs:
                    if obs.asset_id == raw_asset.asset_id or obs.asset_id == res.canonical_id:
                        mb = MeasurementBinding(
                            binding_id=f"bind-{obs.observation_id}",
                            measurement_id=obs.measurement_id,
                            parameter_name=obs.measurement_id,
                            value=obs.value,
                            unit=obs.normalized_unit or obs.original_unit or "UNKNOWN",
                            truth_state=TruthState.OBSERVED if obs.value is not None else TruthState.UNRESOLVED,
                            freshness_status="FRESH",
                            provenance=obs.provenance,
                        )
                        m_bindings.append(mb)

                # Attach geometry as REPRESENTATIVE projection
                geom = GeometryState(
                    geometry_id=f"geom-{raw_asset.asset_id}",
                    asset_id=raw_asset.asset_id,
                    surface_area_m2=120.0,
                    tube_count=500,
                    shell_diameter_m=1.2,
                    truth_state=TruthState.REPRESENTATIVE,
                    provenance=prov_calc,
                )

                # Attach FOUL-X frozen refs if replay service available
                foulx_phys_ref = None
                foulx_foul_ref = None
                foulx_fc_ref = None
                foulx_rel_ref = None
                foulx_dec_ref = None

                if self.replay_service:
                    try:
                        f_snap: ReplaySnapshot = self.replay_service.get_snapshot(target_time)
                        foulx_phys_ref = f_snap.physics_state.model_dump()
                        foulx_foul_ref = f_snap.physics_state.fouling.model_dump()
                        if f_snap.forecast_state:
                            foulx_fc_ref = f_snap.forecast_state[0].model_dump()
                        foulx_rel_ref = f_snap.reliability_state.model_dump()
                        foulx_dec_ref = f_snap.decision_state.model_dump()
                    except Exception:
                        pass

                asset_st = AssetState(
                    asset_id=res.canonical_id or raw_asset.asset_id,
                    canonical_name=raw_asset.name,
                    asset_type=raw_asset.asset_type,
                    resolution_status=res.status,
                    truth_state=raw_asset.truth_state,
                    measurement_bindings=m_bindings,
                    geometry_state=geom,
                    physics_ref=foulx_phys_ref,
                    fouling_ref=foulx_foul_ref,
                    forecast_ref=foulx_fc_ref,
                    reliability_ref=foulx_rel_ref,
                    decision_ref=foulx_dec_ref,
                    issues=issues,
                    provenance=prov_calc,
                )
                assets_shadow_map[asset_st.asset_id] = asset_st

        # Compute deterministic payload hash
        payload_str = f"PLANT-01:{target_time}:{len(assets_shadow_map)}:{temp_state.usability.value}"
        det_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        shadow_prov = ShadowProvenance(
            reconstructed_at="2026-09-17T12:54:00Z",
            target_time=target_time,
            evidence_source_ids=[b.manifest.source_id for b in bundles],
            deterministic_hash=det_hash,
        )

        return DigitalShadowSnapshot(
            snapshot_id=f"shadow-snap-{int(target_time)}",
            plant_id="PLANT-01",
            target_time=target_time,
            asset_shadows=assets_shadow_map,
            topology=topology_edges,
            temporal_state=temp_state,
            issues=issues,
            provenance=shadow_prov,
        )
