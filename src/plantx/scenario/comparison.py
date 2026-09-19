"""Baseline vs Scenario comparative evaluation module for Stage 9."""

from typing import Dict, Any, Optional
from src.plantx.domain.truth_state import TruthState
from src.plantx.domain.provenance import Provenance, ProvenanceType
from src.plantx.scenario.schemas import ScenarioResult, ApplicabilityClassification


class ScenarioComparisonEngine:
    """Calculates deterministic deltas and relative deltas between baseline and scenario states."""

    @staticmethod
    def compare_variable(
        var_name: str,
        baseline_val: Optional[float],
        scenario_val: Optional[float],
        unit: str,
        asset_id: str,
        timestamp: float,
        applicability: ApplicabilityClassification = ApplicabilityClassification.SUPPORTED,
    ) -> ScenarioResult:
        prov = Provenance(
            provenance_id=f"prov-comp-{var_name}-{asset_id}-{int(timestamp)}",
            provenance_type=ProvenanceType.CALCULATION,
            source_reference="ScenarioComparisonEngine",
            timestamp="2026-09-17T14:32:00Z",
            transformation_applied="Baseline vs Scenario Delta Calculation",
        )

        if baseline_val is None or scenario_val is None:
            return ScenarioResult(
                result_id=f"res-{var_name}-{asset_id}-{int(timestamp)}",
                variable=var_name,
                baseline_value=baseline_val,
                scenario_value=scenario_val,
                delta=None,
                relative_delta=None,
                unit=unit,
                truth_state=TruthState.SIMULATED,
                applicability=ApplicabilityClassification.UNAVAILABLE,
                provenance=prov,
            )

        delta = float(scenario_val - baseline_val)
        rel_delta = None
        if abs(baseline_val) > 1e-12:
            rel_delta = float(delta / baseline_val)

        return ScenarioResult(
            result_id=f"res-{var_name}-{asset_id}-{int(timestamp)}",
            variable=var_name,
            baseline_value=baseline_val,
            scenario_value=scenario_val,
            delta=delta,
            relative_delta=rel_delta,
            unit=unit,
            truth_state=TruthState.SIMULATED,
            applicability=applicability,
            provenance=prov,
        )
