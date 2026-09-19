"""Unit normalization and detection engine for PLANT-X."""

from typing import Optional, Tuple
from pydantic import BaseModel, Field
from src.plantx.domain.provenance import Provenance


class NormalizedUnitResult(BaseModel):
    original_value: float
    original_unit: str
    normalized_value: Optional[float]
    normalized_unit: Optional[str]
    conversion_method: str
    conversion_version: str = "1.0.0"
    unit_status: str  # RESOLVED or UNIT_UNRESOLVED
    provenance: Provenance


class UnitNormalizer:
    """Conservative unit detection and normalization."""

    TEMPERATURE_CONVERSIONS = {
        "C": lambda c: c + 273.15,
        "DEG C": lambda c: c + 273.15,
        "DEGC": lambda c: c + 273.15,
        "CELSIUS": lambda c: c + 273.15,
        "K": lambda k: k,
        "KELVIN": lambda k: k,
        "F": lambda f: (f - 32) * 5/9 + 273.15,
        "FAHRENHEIT": lambda f: (f - 32) * 5/9 + 273.15,
    }

    @classmethod
    def normalize_value(cls, val: float, unit_str: str, prov: Provenance) -> NormalizedUnitResult:
        clean_unit = unit_str.strip().upper()
        if clean_unit in cls.TEMPERATURE_CONVERSIONS:
            norm_val = cls.TEMPERATURE_CONVERSIONS[clean_unit](val)
            return NormalizedUnitResult(
                original_value=val,
                original_unit=unit_str,
                normalized_value=norm_val,
                normalized_unit="K",
                conversion_method=f"CONVERT_{clean_unit}_TO_K",
                unit_status="RESOLVED",
                provenance=prov,
            )
        
        # Ambiguous or unknown units must become UNIT_UNRESOLVED
        return NormalizedUnitResult(
            original_value=val,
            original_unit=unit_str,
            normalized_value=None,
            normalized_unit=None,
            conversion_method="NONE",
            unit_status="UNIT_UNRESOLVED",
            provenance=prov,
        )
