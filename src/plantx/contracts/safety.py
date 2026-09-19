"""Safety contract prohibiting autonomous operational actions."""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class SafetyViolationError(Exception):
    """Raised when an illegal autonomous operational command is attempted."""
    pass


class OperationalAction(BaseModel):
    action_type: str
    target_equipment: str
    command_payload: Dict[str, Any]
    requires_human_approval: bool = True
    human_approved: bool = False


class SafetyContract:
    """Enforces non-negotiable advisory safety boundary."""

    PROHIBITED_AUTONOMOUS_ACTIONS = {
        "SHUTDOWN",
        "SETPOINT_CHANGE",
        "MAINTENANCE_EXECUTION",
        "CHEMICAL_DOSING",
        "VALVE_MANIPULATION",
        "PROCESS_MANIPULATION",
    }

    @classmethod
    def validate_action(cls, action: OperationalAction) -> None:
        if action.action_type.upper() in cls.PROHIBITED_AUTONOMOUS_ACTIONS:
            if not action.human_approved:
                raise SafetyViolationError(
                    f"CRITICAL SAFETY VIOLATION: Autonomous operational action '{action.action_type}' "
                    f"on equipment '{action.target_equipment}' is strictly prohibited without explicit human approval."
                )
