"""Economic cost model for Stage 10 Decision Intelligence."""

from typing import Dict, Any, Optional
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.decision.schemas import TotalCostModel, CostComponent, CostComponentStatus


class CostModelEngine:
    """
    Evaluates TotalCostModel strictly using supplied site-specific economic inputs.
    Fails safely with ECONOMIC_ANALYSIS_UNAVAILABLE if inputs are missing.
    Never fabricates monetary values or energy prices.
    """

    @staticmethod
    def evaluate_cost_model(
        asset_id: str,
        timestamp: float,
        site_inputs: Optional[Dict[str, float]] = None,
    ) -> TotalCostModel:
        prov = Provenance(
            provenance_id=f"prov-cost-{asset_id}-{int(timestamp)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="CostModelEngine",
            timestamp="2026-09-17T14:42:00Z",
            transformation_applied="Stage 10 Total Cost Model Evaluation",
        )

        site_inputs = site_inputs or {}

        # 1. Cleaning Cost
        c_clean_val = site_inputs.get("cleaning_cost")
        c_clean = CostComponent(
            name="cleaning_cost",
            amount=c_clean_val,
            currency="INR",
            unit="INR",
            status=CostComponentStatus.AVAILABLE if c_clean_val is not None else CostComponentStatus.UNAVAILABLE,
            source="SITE_INPUT" if c_clean_val is not None else "SITE_INPUT_REQUIRED",
            truth_state=TruthState.OBSERVED if c_clean_val is not None else TruthState.UNRESOLVED,
            provenance=prov,
        )

        # 2. Downtime Cost
        c_down_val = site_inputs.get("downtime_cost")
        c_down = CostComponent(
            name="downtime_cost",
            amount=c_down_val,
            currency="INR",
            unit="INR",
            status=CostComponentStatus.AVAILABLE if c_down_val is not None else CostComponentStatus.UNAVAILABLE,
            source="SITE_INPUT" if c_down_val is not None else "SITE_INPUT_REQUIRED",
            truth_state=TruthState.OBSERVED if c_down_val is not None else TruthState.UNRESOLVED,
            provenance=prov,
        )

        # 3. Energy Cost
        c_energy_val = site_inputs.get("energy_cost")
        c_energy = CostComponent(
            name="energy_cost",
            amount=c_energy_val,
            currency="INR",
            unit="INR",
            status=CostComponentStatus.AVAILABLE if c_energy_val is not None else CostComponentStatus.UNAVAILABLE,
            source="SITE_INPUT" if c_energy_val is not None else "SITE_INPUT_REQUIRED",
            truth_state=TruthState.OBSERVED if c_energy_val is not None else TruthState.UNRESOLVED,
            provenance=prov,
        )

        # 4. Production Loss
        c_prod_val = site_inputs.get("production_loss_cost")
        c_prod = CostComponent(
            name="production_loss_cost",
            amount=c_prod_val,
            currency="INR",
            unit="INR",
            status=CostComponentStatus.AVAILABLE if c_prod_val is not None else CostComponentStatus.UNAVAILABLE,
            source="SITE_INPUT" if c_prod_val is not None else "SITE_INPUT_REQUIRED",
            truth_state=TruthState.OBSERVED if c_prod_val is not None else TruthState.UNRESOLVED,
            provenance=prov,
        )

        # 5. Risk Cost
        c_risk_val = site_inputs.get("risk_cost")
        c_risk = CostComponent(
            name="risk_cost",
            amount=c_risk_val,
            currency="INR",
            unit="INR",
            status=CostComponentStatus.AVAILABLE if c_risk_val is not None else CostComponentStatus.UNAVAILABLE,
            source="SITE_INPUT" if c_risk_val is not None else "SITE_INPUT_REQUIRED",
            truth_state=TruthState.OBSERVED if c_risk_val is not None else TruthState.UNRESOLVED,
            provenance=prov,
        )

        all_vals = [c_clean_val, c_down_val, c_energy_val, c_prod_val, c_risk_val]
        some_avail = any(v is not None for v in all_vals)
        all_avail = all(v is not None for v in all_vals)

        total_val = sum(v for v in all_vals if v is not None) if some_avail else None

        if all_avail:
            status_summary = "COMPLETE_ECONOMIC_ANALYSIS_AVAILABLE"
        elif some_avail:
            status_summary = "PARTIAL_COST_ANALYSIS (Some site economic components missing)"
        else:
            status_summary = "ECONOMIC_ANALYSIS_UNAVAILABLE (Site economic inputs required)"

        return TotalCostModel(
            c_clean=c_clean,
            c_downtime=c_down,
            c_energy=c_energy,
            c_production_loss=c_prod,
            c_risk=c_risk,
            total_cost=total_val,
            is_complete=all_avail,
            status_summary=status_summary,
        )
