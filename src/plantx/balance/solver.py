"""Master Stage 12 Process Graph Solver & Balance Engine."""

import hashlib
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.process.schemas import PlantModel
from src.plantx.process.graph import PlantGraph
from src.plantx.balance.schemas import (
    BalanceCase,
    BalanceScopeType,
    BalanceStatus,
    BalanceDiagnostic,
    DiagnosticType,
    DiagnosticSeverity,
)
from src.plantx.balance.mass_balance import MassBalanceEngine, ComponentBalanceEngine
from src.plantx.balance.energy_balance import EnergyBalanceEngine
from src.plantx.balance.errors import (
    TemporalBalanceViolation,
    BalanceSourceMutation,
    AutonomousControlViolationError,
)


class BalanceSolver:
    """Master Stage 12 Process Graph Solver & Mass / Energy Balance Engine."""

    @staticmethod
    def solve_balance_case(
        plant_model: PlantModel,
        plant_graph: PlantGraph,
        scope_type: BalanceScopeType,
        scope_id: str,
        timestamp: float,
        baseline_max_time: float = 63999.0,
        data_path: Path = Path("data/raw/heat_exchanger_fouling_dataset.csv"),
        allow_autonomous_control: bool = False,
    ) -> BalanceCase:
        # Enforce safety constraint
        if allow_autonomous_control:
            raise AutonomousControlViolationError("Autonomous control is strictly forbidden.")

        # Source immutability check
        h_before = hashlib.sha256(data_path.read_bytes()).hexdigest()

        if timestamp > baseline_max_time:
            raise TemporalBalanceViolation(f"Timestamp {timestamp} exceeds baseline max time {baseline_max_time}")

        prov = Provenance(
            provenance_id=f"prov-balcase-{scope_id}-{int(timestamp)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="BalanceSolver.solve_balance_case",
            timestamp="2026-09-17T15:25:00Z",
            transformation_applied="Stage 12 Conservation Solving",
        )

        diagnostics: List[BalanceDiagnostic] = []
        missing_inputs: List[str] = []

        # 1. Identify Streams per Scope
        inlet_streams = []
        outlet_streams = []
        internal_streams = []

        if scope_type == BalanceScopeType.EQUIPMENT:
            if scope_id not in plant_model.equipment:
                raise ValueError(f"Equipment ID {scope_id} not found in plant model.")
            eq = plant_model.equipment[scope_id]
            inlet_streams = [plant_model.streams[sid] for sid in eq.inlet_stream_ids if sid in plant_model.streams]
            outlet_streams = [plant_model.streams[sid] for sid in eq.outlet_stream_ids if sid in plant_model.streams]

        elif scope_type == BalanceScopeType.PLANT:
            # Internal stream cancellation for plant boundary
            for s_id, s in plant_model.streams.items():
                if s.source_equipment_id and s.destination_equipment_id:
                    internal_streams.append(s_id)
                elif s.destination_equipment_id and not s.source_equipment_id:
                    inlet_streams.append(s)
                elif s.source_equipment_id and not s.destination_equipment_id:
                    outlet_streams.append(s)

        # 2. Check recycle topology in plant graph
        try:
            cycles = [edge for edge in plant_graph.edges if edge.relation.value == "RECYCLES_TO"]
            if cycles:
                diagnostics.append(
                    BalanceDiagnostic(
                        diagnostic_id=f"diag-recycle-{scope_id}",
                        diagnostic_type=DiagnosticType.RECYCLE_PRESENT,
                        severity=DiagnosticSeverity.INFO,
                        description="Recycle loop detected in process topology. Iterative nonlinear solver withheld in Stage 12.",
                        provenance=prov,
                    )
                )
        except Exception:
            pass

        # 3. Evaluate Mass Balance
        mass_res = MassBalanceEngine.evaluate_mass_balance(inlet_streams, outlet_streams, timestamp)

        # 4. Evaluate Component Balance
        comp_res = ComponentBalanceEngine.evaluate_component_balance(inlet_streams, outlet_streams, timestamp)
        if not comp_res:
            missing_inputs.append("Stream chemical composition")
            diagnostics.append(
                BalanceDiagnostic(
                    diagnostic_id=f"diag-comp-{scope_id}",
                    diagnostic_type=DiagnosticType.COMPOSITION_UNAVAILABLE,
                    severity=DiagnosticSeverity.INFO,
                    description="Chemical composition is UNAVAILABLE in source evidence. Component balance withheld without fabrication.",
                    provenance=prov,
                )
            )

        # 5. Evaluate Energy Balance
        energy_res = EnergyBalanceEngine.evaluate_energy_balance(inlet_streams, outlet_streams, timestamp)
        if energy_res.status in [BalanceStatus.PARTIALLY_EVALUATED, BalanceStatus.UNAVAILABLE]:
            missing_inputs.append("Stream enthalpy & pressure drop (ΔP)")
            diagnostics.append(
                BalanceDiagnostic(
                    diagnostic_id=f"diag-enthalpy-{scope_id}",
                    diagnostic_type=DiagnosticType.ENTHALPY_UNAVAILABLE,
                    severity=DiagnosticSeverity.INFO,
                    description="Full stream enthalpy & pressure drop channels missing in dataset. Energy balance evaluated with limitations.",
                    provenance=prov,
                )
            )

        # 6. Overall Status Determination
        if mass_res.status == BalanceStatus.IMBALANCE or energy_res.status == BalanceStatus.IMBALANCE:
            overall_status = BalanceStatus.IMBALANCE
        elif mass_res.status == BalanceStatus.BALANCED and energy_res.status == BalanceStatus.BALANCED:
            overall_status = BalanceStatus.BALANCED
        else:
            overall_status = BalanceStatus.PARTIALLY_EVALUATED

        # Source immutability check after execution
        h_after = hashlib.sha256(data_path.read_bytes()).hexdigest()
        if h_before != h_after:
            raise BalanceSourceMutation("Source dataset mutated during Stage 12 balance solve!")

        # Deterministic result hash computation
        res_data = json.dumps(
            {
                "scope": scope_id,
                "mass_status": mass_res.status.value,
                "energy_status": energy_res.status.value,
                "overall_status": overall_status.value,
            },
            sort_keys=True,
        )
        result_hash = hashlib.sha256(res_data.encode("utf-8")).hexdigest()

        return BalanceCase(
            balance_id=f"bal-{scope_id}-{int(timestamp)}",
            scope_type=scope_type,
            scope_id=scope_id,
            timestamp=timestamp,
            boundary={"scope_id": scope_id, "scope_type": scope_type.value},
            input_streams=[s.stream_id for s in inlet_streams],
            output_streams=[s.stream_id for s in outlet_streams],
            internal_streams=internal_streams,
            mass_balance=mass_res,
            component_balances=comp_res,
            energy_balance=energy_res,
            diagnostics=diagnostics,
            missing_inputs=missing_inputs,
            inconsistencies=[],
            status=overall_status,
            provenance=prov,
            graph_hash=plant_model.graph_hash,
            result_hash=result_hash,
            human_review_required=True,
        )
