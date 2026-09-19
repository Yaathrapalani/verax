"""Energy balance and thermal duty calculator for Stage 12."""

from typing import List, Dict, Any, Optional
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.process.schemas import ProcessStream
from src.plantx.balance.schemas import (
    EnergyBalanceResult,
    EnergyBoundaryTerm,
    BalanceStatus,
)


class EnergyBalanceEngine:
    """Evaluates control-volume energy balance Σ H_in + Q_in - W_out = Σ H_out."""

    @staticmethod
    def evaluate_energy_balance(
        inlet_streams: List[ProcessStream],
        outlet_streams: List[ProcessStream],
        timestamp: float,
        heat_in_val: Optional[float] = None,
        heat_out_val: Optional[float] = None,
        work_in_val: Optional[float] = None,
        work_out_val: Optional[float] = None,
        tolerance: float = 0.02,
    ) -> EnergyBalanceResult:
        prov = Provenance(
            provenance_id=f"prov-energybal-{int(timestamp)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="EnergyBalanceEngine.evaluate_energy_balance",
            timestamp="2026-09-17T15:25:00Z",
            transformation_applied="Stage 12 Energy Balance Evaluation",
        )

        # Enthalpy flows (kW = mass_flow * enthalpy or derived heat duty)
        in_enthalpies = [s.enthalpy for s in inlet_streams if s.enthalpy is not None]
        out_enthalpies = [s.enthalpy for s in outlet_streams if s.enthalpy is not None]

        h_in_avail = len(in_enthalpies) == len(inlet_streams) and len(inlet_streams) > 0
        h_out_avail = len(out_enthalpies) == len(outlet_streams) and len(outlet_streams) > 0

        heat_in_term = EnergyBoundaryTerm(
            term_name="Q_IN",
            value=heat_in_val,
            unit="kW",
            source="SITE_INPUT" if heat_in_val is not None else "UNAVAILABLE",
            truth_state=TruthState.OBSERVED if heat_in_val is not None else TruthState.UNRESOLVED,
            provenance=prov,
        )

        heat_out_term = EnergyBoundaryTerm(
            term_name="Q_OUT",
            value=heat_out_val,
            unit="kW",
            source="SITE_INPUT" if heat_out_val is not None else "UNAVAILABLE",
            truth_state=TruthState.OBSERVED if heat_out_val is not None else TruthState.UNRESOLVED,
            provenance=prov,
        )

        if not h_in_avail or not h_out_avail:
            return EnergyBalanceResult(
                total_enthalpy_in=sum(in_enthalpies) if in_enthalpies else None,
                total_enthalpy_out=sum(out_enthalpies) if out_enthalpies else None,
                heat_in=heat_in_term,
                heat_out=heat_out_term,
                accumulation=0.0,
                residual=None,
                relative_residual=None,
                tolerance=tolerance,
                status=BalanceStatus.BALANCED_WITH_LIMITATIONS if (in_enthalpies or out_enthalpies) else BalanceStatus.PARTIALLY_EVALUATED,
                inputs=[s.stream_id for s in inlet_streams + outlet_streams],
                provenance=prov,
            )

        tot_h_in = sum(in_enthalpies) + (heat_in_val or 0.0) + (work_in_val or 0.0)
        tot_h_out = sum(out_enthalpies) + (heat_out_val or 0.0) + (work_out_val or 0.0)
        residual = tot_h_in - tot_h_out
        denom = max(abs(tot_h_in), abs(tot_h_out), 1e-6)
        rel_residual = abs(residual) / denom

        if rel_residual <= tolerance:
            status = BalanceStatus.BALANCED
        else:
            status = BalanceStatus.IMBALANCE

        return EnergyBalanceResult(
            total_enthalpy_in=tot_h_in,
            total_enthalpy_out=tot_h_out,
            heat_in=heat_in_term,
            heat_out=heat_out_term,
            accumulation=0.0,
            residual=residual,
            relative_residual=rel_residual,
            tolerance=tolerance,
            status=status,
            inputs=[s.stream_id for s in inlet_streams + outlet_streams],
            provenance=prov,
        )
