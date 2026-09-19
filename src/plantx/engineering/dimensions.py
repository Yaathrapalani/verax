"""Dimensional classifications and unit registries for Stage 5 Engineering Core."""

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class DimensionCategory(str, Enum):
    MASS = "MASS"
    TIME = "TIME"
    TEMPERATURE = "TEMPERATURE"
    PRESSURE = "PRESSURE"
    ENERGY = "ENERGY"
    POWER = "POWER"
    VOLUME = "VOLUME"
    LENGTH = "LENGTH"
    AREA = "AREA"
    MASS_FLOW = "MASS_FLOW"
    VOLUME_FLOW = "VOLUME_FLOW"
    ENERGY_FLOW = "ENERGY_FLOW"
    HEAT_TRANSFER_COEFFICIENT = "HEAT_TRANSFER_COEFFICIENT"
    THERMAL_RESISTANCE = "THERMAL_RESISTANCE"
    DIMENSIONLESS = "DIMENSIONLESS"


class EngineeringUnitRegistry:
    """Registry mapping unit strings to canonical SI dimensions and conversion factors."""

    UNIT_DIMENSIONS: Dict[str, DimensionCategory] = {
        "K": DimensionCategory.TEMPERATURE,
        "C": DimensionCategory.TEMPERATURE,
        "DEG C": DimensionCategory.TEMPERATURE,
        "DEGC": DimensionCategory.TEMPERATURE,
        "F": DimensionCategory.TEMPERATURE,
        "KG/S": DimensionCategory.MASS_FLOW,
        "KG/H": DimensionCategory.MASS_FLOW,
        "M3/S": DimensionCategory.VOLUME_FLOW,
        "KW": DimensionCategory.POWER,
        "MW": DimensionCategory.POWER,
        "W": DimensionCategory.POWER,
        "J": DimensionCategory.ENERGY,
        "KJ": DimensionCategory.ENERGY,
        "M2": DimensionCategory.AREA,
        "M2K/W": DimensionCategory.THERMAL_RESISTANCE,
        "W/M2K": DimensionCategory.HEAT_TRANSFER_COEFFICIENT,
        "BAR": DimensionCategory.PRESSURE,
        "KPA": DimensionCategory.PRESSURE,
        "PA": DimensionCategory.PRESSURE,
        "PSI": DimensionCategory.PRESSURE,
        "FRACTION": DimensionCategory.DIMENSIONLESS,
    }

    @classmethod
    def get_dimension(cls, unit_str: str) -> Optional[DimensionCategory]:
        if not unit_str or unit_str.upper() in {"UNKNOWN", "UNIT_UNRESOLVED"}:
            return None
        return cls.UNIT_DIMENSIONS.get(unit_str.strip().upper())
