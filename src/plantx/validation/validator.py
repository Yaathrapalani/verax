"""Validation engine for PLANT-X domain model."""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from src.plantx.domain import Plant, Asset, Measurement, Stream, TruthState


class ValidationErrorType(str, Enum):
    MISSING_IDENTIFIER = "MISSING_IDENTIFIER"
    DUPLICATE_IDENTITY = "DUPLICATE_IDENTITY"
    INVALID_UNIT = "INVALID_UNIT"
    IMPOSSIBLE_VALUE = "IMPOSSIBLE_VALUE"
    MISSING_PROVENANCE = "MISSING_PROVENANCE"
    INVALID_RELATIONSHIP = "INVALID_RELATIONSHIP"
    ORPHAN_MEASUREMENT = "ORPHAN_MEASUREMENT"
    CONTRADICTORY_TRUTH_STATE = "CONTRADICTORY_TRUTH_STATE"
    INVALID_TIMESTAMP = "INVALID_TIMESTAMP"
    MALFORMED_REFERENCE = "MALFORMED_REFERENCE"


class StructuredValidationError(BaseModel):
    error_type: ValidationErrorType
    entity_id: str
    field: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class PlantValidator:
    """Validates structural integrity, truth states, unit safety, and graph relationships."""

    VALID_UNITS = {"K", "C", "bar", "kPa", "kg/s", "kW", "m2", "m2K/W", "USD", "hours", "fraction"}

    @classmethod
    def validate_plant_topology(
        cls,
        plant: Plant,
        assets: List[Asset],
        measurements: List[Measurement],
        streams: List[Stream],
    ) -> List[StructuredValidationError]:
        errors: List[StructuredValidationError] = []

        # 1. Identifier & Duplicate Asset check
        asset_ids = set()
        for a in assets:
            if not a.asset_id:
                errors.append(
                    StructuredValidationError(
                        error_type=ValidationErrorType.MISSING_IDENTIFIER,
                        entity_id="UNKNOWN",
                        field="asset_id",
                        message="Asset missing required identifier.",
                    )
                )
            elif a.asset_id in asset_ids:
                errors.append(
                    StructuredValidationError(
                        error_type=ValidationErrorType.DUPLICATE_IDENTITY,
                        entity_id=a.asset_id,
                        field="asset_id",
                        message=f"Duplicate asset identifier detected: {a.asset_id}",
                    )
                )
            asset_ids.add(a.asset_id)

        # 2. Measurement validation
        stream_ids = {s.stream_id for s in streams}
        for m in measurements:
            # Check unit validity
            if m.unit not in cls.VALID_UNITS:
                errors.append(
                    StructuredValidationError(
                        error_type=ValidationErrorType.INVALID_UNIT,
                        entity_id=m.measurement_id,
                        field="unit",
                        message=f"Invalid unit '{m.unit}' for measurement {m.measurement_id}",
                    )
                )

            # Check impossible values (e.g. Kelvin < 0)
            if m.unit == "K" and m.value < 0:
                errors.append(
                    StructuredValidationError(
                        error_type=ValidationErrorType.IMPOSSIBLE_VALUE,
                        entity_id=m.measurement_id,
                        field="value",
                        message=f"Temperature below 0 K: {m.value}",
                    )
                )

            # Check provenance requirement
            if m.provenance is None:
                errors.append(
                    StructuredValidationError(
                        error_type=ValidationErrorType.MISSING_PROVENANCE,
                        entity_id=m.measurement_id,
                        field="provenance",
                        message=f"Measurement {m.measurement_id} missing mandatory provenance.",
                    )
                )

            # Check orphan measurement
            if m.stream_id not in stream_ids and m.stream_id != "UNASSIGNED":
                errors.append(
                    StructuredValidationError(
                        error_type=ValidationErrorType.ORPHAN_MEASUREMENT,
                        entity_id=m.measurement_id,
                        field="stream_id",
                        message=f"Measurement {m.measurement_id} points to non-existent stream {m.stream_id}.",
                    )
                )

            # Check contradictory truth states
            if m.truth_state == TruthState.OBSERVED and m.provenance and m.provenance.provenance_type.value == "CALCULATION":
                errors.append(
                    StructuredValidationError(
                        error_type=ValidationErrorType.CONTRADICTORY_TRUTH_STATE,
                        entity_id=m.measurement_id,
                        field="truth_state",
                        message="Contradiction: Truth state is OBSERVED but provenance source is CALCULATION.",
                    )
                )

        return errors
