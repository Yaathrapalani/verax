"""Stage 12 exception definitions for Process Graph Solver & Mass/Energy Balance Engine."""


class TemporalBalanceViolation(Exception):
    """Raised when balance solver uses future evidence beyond evaluation timestamp T."""
    pass


class BalanceSourceMutation(Exception):
    """Raised when underlying source evidence dataset is mutated during balance solving."""
    pass


class BalanceValidationError(Exception):
    """Raised when balance solver receives invalid topology, dimensions, or conflicting inputs."""
    pass


class AutonomousControlViolationError(Exception):
    """Raised when autonomous plant control, setpoint changes, or automatic commands are requested."""
    pass
