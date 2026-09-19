"""Scenario catalog and metadata definitions for Stage 9."""

from typing import Dict, Any, List
from src.plantx.scenario.schemas import ScenarioType

SCENARIO_CATALOG_DEFS: Dict[ScenarioType, Dict[str, Any]] = {
    ScenarioType.FLOW_INCREASE: {
        "allowed_min_delta": -0.50,
        "allowed_max_delta": 0.50,
        "default_magnitude": 0.15,
        "description": "Hypothetical increase in operating crude tube/shell mass flow rate.",
        "required_inputs": ["m_kg_s"],
    },
    ScenarioType.FLOW_DECREASE: {
        "allowed_min_delta": -0.50,
        "allowed_max_delta": 0.50,
        "default_magnitude": -0.15,
        "description": "Hypothetical decrease in operating crude tube/shell mass flow rate.",
        "required_inputs": ["m_kg_s"],
    },
    ScenarioType.HEAT_TRANSFER_DEGRADATION: {
        "allowed_min_delta": 0.0,
        "allowed_max_delta": 0.50,
        "default_magnitude": 0.10,
        "description": "Hypothetical degradation in overall heat conductance UA.",
        "required_inputs": ["UA"],
    },
    ScenarioType.FOULING_ACCELERATION: {
        "allowed_min_delta": 0.0,
        "allowed_max_delta": 5.0,
        "default_magnitude": 0.50,
        "description": "Hypothetical acceleration in derived thermal fouling resistance Rf growth rate.",
        "required_inputs": ["Rf_derived"],
    },
    ScenarioType.SENSOR_UNAVAILABLE: {
        "allowed_min_delta": 0.0,
        "allowed_max_delta": 1.0,
        "default_magnitude": 1.0,
        "description": "Hypothetical sensor measurement outage testing information degradation.",
        "required_inputs": ["sensor_tag"],
    },
    ScenarioType.FEED_PROPERTY_SHIFT: {
        "allowed_min_delta": -0.30,
        "allowed_max_delta": 0.30,
        "default_magnitude": 0.10,
        "description": "Hypothetical shift in feed crude oil API gravity or heat capacity.",
        "required_inputs": ["Crude_API"],
    },
    ScenarioType.COMBINED_OPERATING_SHIFT: {
        "allowed_min_delta": -0.50,
        "allowed_max_delta": 0.50,
        "default_magnitude": 0.15,
        "description": "Controlled combination of supported flow and thermal perturbations.",
        "required_inputs": ["m_kg_s", "UA"],
    },
}
