"""Mass and Component Balance Calculators for Stage 12."""

from typing import List, Dict, Any, Tuple
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.process.schemas import ProcessStream, StreamPhase
from src.plantx.balance.schemas import (
    MassBalanceResult,
    ComponentBalanceResult,
    BalanceStatus,
)


class MassBalanceEngine:
    """Evaluates material conservation Σ mass_in - Σ mass_out = accumulation."""

    @staticmethod
    def evaluate_mass_balance(
        inlet_streams: List[ProcessStream],
        outlet_streams: List[ProcessStream],
        timestamp: float,
        tolerance: float = 0.01,
    ) -> MassBalanceResult:
        prov = Provenance(
            provenance_id=f"prov-massbal-{int(timestamp)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="MassBalanceEngine.evaluate_mass_balance",
            timestamp="2026-09-17T15:25:00Z",
            transformation_applied="Stage 12 Steady-State Mass Balance",
        )

        in_flows = [s.mass_flow for s in inlet_streams if s.mass_flow is not None]
        out_flows = [s.mass_flow for s in outlet_streams if s.mass_flow is not None]

        all_in_avail = len(in_flows) == len(inlet_streams) and len(inlet_streams) > 0
        all_out_avail = len(out_flows) == len(outlet_streams) and len(outlet_streams) > 0

        if not all_in_avail or not all_out_avail:
            return MassBalanceResult(
                total_in=sum(in_flows) if in_flows else None,
                total_out=sum(out_flows) if out_flows else None,
                accumulation=0.0,
                residual=None,
                relative_residual=None,
                tolerance=tolerance,
                status=BalanceStatus.PARTIALLY_EVALUATED,
                inputs=[s.stream_id for s in inlet_streams + outlet_streams],
                provenance=prov,
            )

        total_in = sum(in_flows)
        total_out = sum(out_flows)
        residual = total_in - total_out
        denom = max(abs(total_in), abs(total_out), 1e-6)
        rel_residual = abs(residual) / denom

        if rel_residual <= tolerance:
            status = BalanceStatus.BALANCED
        else:
            status = BalanceStatus.IMBALANCE

        return MassBalanceResult(
            total_in=total_in,
            total_out=total_out,
            accumulation=0.0,
            residual=residual,
            relative_residual=rel_residual,
            tolerance=tolerance,
            status=status,
            inputs=[s.stream_id for s in inlet_streams + outlet_streams],
            provenance=prov,
        )


class ComponentBalanceEngine:
    """Evaluates component mass conservation if stream compositions exist."""

    @staticmethod
    def evaluate_component_balance(
        inlet_streams: List[ProcessStream],
        outlet_streams: List[ProcessStream],
        timestamp: float,
    ) -> Dict[str, ComponentBalanceResult]:
        results = {}
        prov = Provenance(
            provenance_id=f"prov-compbal-{int(timestamp)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="ComponentBalanceEngine",
            timestamp="2026-09-17T15:25:00Z",
        )

        all_streams = inlet_streams + outlet_streams
        components = set()
        for s in all_streams:
            components.update(s.composition.keys())

        if not components:
            return {}

        for comp in components:
            in_comp_flow = sum(s.mass_flow * s.composition[comp].value for s in inlet_streams if s.mass_flow and comp in s.composition)
            out_comp_flow = sum(s.mass_flow * s.composition[comp].value for s in outlet_streams if s.mass_flow and comp in s.composition)

            res = in_comp_flow - out_comp_flow
            results[comp] = ComponentBalanceResult(
                component_name=comp,
                total_in=in_comp_flow,
                total_out=out_comp_flow,
                residual=res,
                status=BalanceStatus.BALANCED if abs(res) < 1e-4 else BalanceStatus.IMBALANCE,
                provenance=prov,
            )

        return results
