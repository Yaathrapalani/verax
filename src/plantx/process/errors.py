"""Stage 11 exception definitions for Process Model & Computational Plant Graph."""


class TemporalProcessGraphViolation(Exception):
    """Raised when process graph model references future evidence beyond evaluation timestamp T."""
    pass


class ProcessSourceMutation(Exception):
    """Raised when underlying source evidence dataset is mutated during process graph construction."""
    pass


class TopologyValidationError(Exception):
    """Raised when computational plant graph topology contains invalid structures or orphan nodes."""
    pass


class AutonomousControlViolationError(Exception):
    """Raised when autonomous plant control, setpoint changes, or automatic commands are requested."""
    pass
