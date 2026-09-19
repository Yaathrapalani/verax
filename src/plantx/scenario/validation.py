"""Scenario parameter and perturbation validator for Stage 9."""

from typing import Dict, Any, List
from src.plantx.scenario.schemas import ScenarioType, ScenarioParameter
from src.plantx.scenario.scenario_types import SCENARIO_CATALOG_DEFS
from src.plantx.scenario.errors import UnsupportedPerturbationError


class ScenarioValidator:
    """Validates scenario types, perturbation magnitudes, and input parameters against prototype scenario bounds."""

    @staticmethod
    def validate_perturbation(scenario_type: ScenarioType, magnitude: float) -> bool:
        cat_def = SCENARIO_CATALOG_DEFS.get(scenario_type)
        if not cat_def:
            raise UnsupportedPerturbationError(f"Unsupported scenario type '{scenario_type}'")

        min_allowed = cat_def["allowed_min_delta"]
        max_allowed = cat_def["allowed_max_delta"]

        if magnitude < min_allowed or magnitude > max_allowed:
            raise UnsupportedPerturbationError(
                f"Perturbation magnitude {magnitude:.4f} for scenario {scenario_type.value} "
                f"exceeds allowed prototype scenario bounds [{min_allowed}, {max_allowed}]. "
                "Silently clamping or executing out-of-bound scenarios is strictly forbidden."
            )
        return True
