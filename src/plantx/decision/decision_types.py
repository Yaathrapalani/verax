"""Decision options definition catalog for Stage 10."""

from typing import Dict, Any, List
from src.plantx.decision.schemas import DecisionOptionType

DECISION_OPTION_CATALOG: Dict[DecisionOptionType, Dict[str, Any]] = {
    DecisionOptionType.D1_CONTINUE_OPERATION: {
        "name": "CONTINUE_OPERATION",
        "description": "Continue standard thermal operation under active telemetry monitoring.",
        "known_consequences": ["Continued fouling trajectory", "Continued thermal degradation"],
        "unknown_consequences": ["Exact future cleaning window boundary"],
    },
    DecisionOptionType.D2_CLEANING_REVIEW: {
        "name": "CLEANING_REVIEW",
        "description": "Trigger engineering and operations review for heat exchanger cleaning.",
        "known_consequences": ["Downtime requirement if scheduled", "Potential thermal performance recovery"],
        "unknown_consequences": ["Exact site contractor availability"],
    },
    DecisionOptionType.D3_SCHEDULED_CLEANING: {
        "name": "SCHEDULED_CLEANING",
        "description": "Schedule exchanger cleaning during upcoming turnaround window.",
        "known_consequences": ["Cleaning expenditure", "Restoration of clean UA baseline"],
        "unknown_consequences": ["Turnaround duration variance"],
    },
    DecisionOptionType.D4_INVESTIGATE_BEFORE_CLEANING: {
        "name": "INVESTIGATE_BEFORE_CLEANING",
        "description": "Obtain discriminating evidence (e.g. ΔP history or lab analysis) before committing to cleaning.",
        "known_consequences": ["Additional evidence acquisition", "Uncertainty reduction"],
        "unknown_consequences": ["Lab sample turnaround time"],
    },
    DecisionOptionType.D5_DEFER_DECISION: {
        "name": "DEFER_DECISION",
        "description": "Defer decision to next 24-hour evaluation cycle.",
        "known_consequences": ["Delayed intervention", "Future reassessment"],
        "unknown_consequences": ["Incremental fouling accumulation during deferral"],
    },
}
