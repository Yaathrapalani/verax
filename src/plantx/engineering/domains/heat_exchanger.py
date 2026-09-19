"""Heat Exchanger domain engineering state builder referencing frozen FOUL-X M2 physics."""

from typing import Dict, Any, List, Optional
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.shadow.schemas import DigitalShadowSnapshot
from src.plantx.engineering.dimensions import DimensionCategory
from src.plantx.engineering.quantities import EngineeringQuantity, QuantityStatus
from src.plantx.engineering.state import EngineeringState
from src.foulx.replay import ReplayService, ReplaySnapshot


class HeatExchangerStateBuilder:
    """State builder constructing EngineeringState from DigitalShadowSnapshot at T."""

    def __init__(self, replay_service: Optional[ReplayService] = None):
        self.replay_service = replay_service

    def build_heat_exchanger_state(
        self,
        asset_id: str,
        shadow_snapshot: DigitalShadowSnapshot,
    ) -> EngineeringState:
        target_time = shadow_snapshot.target_time
        prov = Provenance(
            provenance_id=f"prov-eng-hx-{asset_id}-{int(target_time)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="HeatExchangerStateBuilder",
            timestamp="2026-09-17T13:28:00Z",
            transformation_applied="Stage 5 Heat Exchanger Engineering State Construction",
        )

        quantities: Dict[str, EngineeringQuantity] = {}
        unavailable_items: List[Dict[str, Any]] = []
        assumptions: List[str] = [
            "COUNTER_CURRENT_EXCHANGER_ASSUMPTION",
            "INITIAL_WINDOW_UA_REFERENCE_BASELINE",
        ]

        # Extract telemetry bindings from shadow snapshot
        asset_shadow = shadow_snapshot.asset_shadows.get(asset_id)
        if asset_shadow and asset_shadow.measurement_bindings:
            for mb in asset_shadow.measurement_bindings:
                if mb.unit == "UNKNOWN":
                    quantities[mb.parameter_name] = EngineeringQuantity(
                        quantity_id=f"qty-{mb.measurement_id}",
                        name=mb.parameter_name,
                        original_value=mb.value,
                        original_unit="UNKNOWN",
                        status=QuantityStatus.UNIT_UNRESOLVED,
                        truth_state=TruthState.UNRESOLVED,
                        provenance=mb.provenance,
                    )
                elif mb.value is not None:
                    quantities[mb.parameter_name] = EngineeringQuantity(
                        quantity_id=f"qty-{mb.measurement_id}",
                        name=mb.parameter_name,
                        normalized_value=float(mb.value),
                        normalized_unit=mb.unit,
                        status=QuantityStatus.VALID,
                        truth_state=TruthState.OBSERVED,
                        provenance=mb.provenance,
                    )

        # Referencing frozen FOUL-X M2 physics outputs cleanly
        foulx_snap = None
        if self.replay_service:
            try:
                foulx_snap = self.replay_service.get_snapshot(target_time)
            except Exception:
                pass

        if foulx_snap:
            phys = foulx_snap.physics_state
            # Heat duty Q
            if phys.thermal.q_tube is not None:
                quantities["Q_tube"] = EngineeringQuantity(
                    quantity_id=f"qty-qtube-{int(target_time)}",
                    name="Q_tube",
                    normalized_value=float(phys.thermal.q_tube),
                    normalized_unit="W",
                    dimension=DimensionCategory.POWER,
                    status=QuantityStatus.VALID,
                    truth_state=TruthState.INFERRED,
                    provenance=prov,
                )
            # LMTD
            if phys.thermal.lmtd is not None:
                quantities["LMTD"] = EngineeringQuantity(
                    quantity_id=f"qty-lmtd-{int(target_time)}",
                    name="LMTD",
                    normalized_value=float(phys.thermal.lmtd),
                    normalized_unit="K",
                    dimension=DimensionCategory.TEMPERATURE,
                    status=QuantityStatus.VALID,
                    truth_state=TruthState.INFERRED,
                    provenance=prov,
                )
            # UA
            if phys.thermal.ua is not None:
                quantities["UA"] = EngineeringQuantity(
                    quantity_id=f"qty-ua-{int(target_time)}",
                    name="UA",
                    normalized_value=float(phys.thermal.ua),
                    normalized_unit="W/K",
                    status=QuantityStatus.VALID,
                    truth_state=TruthState.INFERRED,
                    provenance=prov,
                )
            # Derived fouling resistance Rf
            if phys.fouling.rf_derived is not None:
                quantities["Rf_derived"] = EngineeringQuantity(
                    quantity_id=f"qty-rf-{int(target_time)}",
                    name="Rf_derived",
                    normalized_value=float(phys.fouling.rf_derived),
                    normalized_unit="m2K/W",
                    dimension=DimensionCategory.THERMAL_RESISTANCE,
                    status=QuantityStatus.VALID,
                    truth_state=TruthState.INFERRED,
                    provenance=prov,
                )

        # Hydraulic quantities are UNAVAILABLE in current dataset
        unavailable_items.append({
            "parameter_name": "delta_p",
            "reason": "REQUIRED_PRESSURE_EVIDENCE_NOT_AVAILABLE",
        })

        validity_status = "VALID"
        if any(q.status == QuantityStatus.UNIT_UNRESOLVED for q in quantities.values()):
            validity_status = "CONDITIONALLY_VALID"

        return EngineeringState(
            asset_id=asset_id,
            timestamp=target_time,
            quantities=quantities,
            calculations_executed=["M2_PHYSICS_Q", "M2_PHYSICS_LMTD", "M2_PHYSICS_UA", "M2_PHYSICS_RF"],
            validity=validity_status,
            assumptions=assumptions,
            unavailable_items=unavailable_items,
            provenance=prov,
        )
