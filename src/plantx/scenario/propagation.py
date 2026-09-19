"""Engineering state recalculation and propagation via Stage 5 Engineering Core."""

from typing import Dict, Any, Tuple
from src.physics.state_estimator import PhysicsStateEstimator, EXCHANGER_MAPPING
from src.physics.schemas import CanonicalExchangerState, StateValidity
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.engineering.quantities import EngineeringQuantity, QuantityStatus
from src.plantx.engineering.state import EngineeringState


class ScenarioPropagationEngine:
    """Propagates scenario perturbations cleanly through trusted Stage 5 calculations."""

    def __init__(self, physics_estimator: PhysicsStateEstimator = None):
        self.physics_estimator = physics_estimator or PhysicsStateEstimator()

    def propagate_scenario(
        self,
        raw_record: Dict[str, Any],
        asset_id: str,
        perturbed_record: Dict[str, Any],
    ) -> Tuple[CanonicalExchangerState, EngineeringState]:
        """
        Recalculates canonical exchanger state and engineering state for perturbed record.
        Reuses trusted Stage 5 calculation paths.
        """
        if not self.physics_estimator.ua_clean_references:
            # Baseline reference default if not fitted
            self.physics_estimator.ua_clean_references = {"E01": 207061.2, "E02": 213435.9, "E03": 195000.0, "E04": 180000.0, "E05": 190000.0}

        # Execute Stage 5 physics process_record
        scenario_canonical = self.physics_estimator.process_record(perturbed_record, exchanger_id=asset_id)

        target_time = float(perturbed_record.get("Time_hr", 0.0))
        prov = Provenance(
            provenance_id=f"prov-scen-eng-{asset_id}-{int(target_time)}",
            provenance_type=ProvenanceType.SIMULATION,
            source_reference="ScenarioPropagationEngine",
            timestamp="2026-09-17T14:32:00Z",
            transformation_applied="Stage 9 Scenario Engineering State Recalculation",
        )

        quantities: Dict[str, EngineeringQuantity] = {}
        phys = scenario_canonical.thermal
        foul = scenario_canonical.fouling

        if phys.q_tube is not None:
            quantities["Q_tube"] = EngineeringQuantity(
                quantity_id=f"qty-scen-qtube-{int(target_time)}",
                name="Q_tube",
                normalized_value=float(phys.q_tube),
                normalized_unit="W",
                status=QuantityStatus.VALID,
                truth_state=TruthState.SIMULATED,
                provenance=prov,
            )

        if phys.lmtd is not None:
            quantities["LMTD"] = EngineeringQuantity(
                quantity_id=f"qty-scen-lmtd-{int(target_time)}",
                name="LMTD",
                normalized_value=float(phys.lmtd),
                normalized_unit="K",
                status=QuantityStatus.VALID,
                truth_state=TruthState.SIMULATED,
                provenance=prov,
            )

        if phys.ua is not None:
            quantities["UA"] = EngineeringQuantity(
                quantity_id=f"qty-scen-ua-{int(target_time)}",
                name="UA",
                normalized_value=float(phys.ua),
                normalized_unit="W/K",
                status=QuantityStatus.VALID,
                truth_state=TruthState.SIMULATED,
                provenance=prov,
            )

        if foul.rf_derived is not None:
            quantities["Rf_derived"] = EngineeringQuantity(
                quantity_id=f"qty-scen-rf-{int(target_time)}",
                name="Rf_derived",
                normalized_value=float(foul.rf_derived),
                normalized_unit="m2K/W",
                status=QuantityStatus.VALID,
                truth_state=TruthState.SIMULATED,
                provenance=prov,
            )

        eng_state = EngineeringState(
            asset_id=asset_id,
            timestamp=target_time,
            quantities=quantities,
            calculations_executed=["M2_PHYSICS_Q", "M2_PHYSICS_LMTD", "M2_PHYSICS_UA", "M2_PHYSICS_RF"],
            validity=scenario_canonical.data_quality.primary_status.value,
            assumptions=["SCENARIO_SIMULATION_PROPAGATION"],
            unavailable_items=[{"parameter_name": "delta_p", "reason": "REQUIRED_PRESSURE_EVIDENCE_NOT_AVAILABLE"}],
            provenance=prov,
        )

        return scenario_canonical, eng_state
