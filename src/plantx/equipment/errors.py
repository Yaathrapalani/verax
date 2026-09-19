"""Stage 14 exception definitions for Equipment Simulation Runtime."""


class TemporalEquipmentViolation(Exception):
    """Raised when equipment simulation uses future evidence beyond evaluation timestamp T."""
    pass


class EquipmentSourceMutation(Exception):
    """Raised when underlying source evidence dataset is mutated during equipment simulation."""
    pass


class EquipmentValidationError(Exception):
    """Raised when invalid equipment inputs, thermal crossing, or zero flows are supplied."""
    pass


class AutonomousControlViolationError(Exception):
    """Raised when autonomous plant control, setpoint changes, or automatic commands are requested."""
    pass
