"""Truth state definitions for PLANT-X domain model."""

from enum import Enum


class TruthState(str, Enum):
    """Canonical truth states representing epistemological status of data/objects."""
    OBSERVED = "OBSERVED"
    INFERRED = "INFERRED"
    REPRESENTATIVE = "REPRESENTATIVE"
    UNRESOLVED = "UNRESOLVED"
    SIMULATED = "SIMULATED"
    ASSUMED = "ASSUMED"
