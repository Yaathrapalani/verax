"""Stage 13 exception definitions for Thermodynamic State & Benchmark Runtime."""


class TemporalThermoViolation(Exception):
    """Raised when thermodynamic calculation uses future evidence beyond evaluation timestamp T."""
    pass


class ThermoSourceMutation(Exception):
    """Raised when underlying source evidence dataset is mutated during thermodynamic processing."""
    pass


class ThermoValidationError(Exception):
    """Raised when invalid thermodynamic state inputs (e.g. T <= 0 K, P < 0, unresolvable component) are supplied."""
    pass


class AutonomousControlViolationError(Exception):
    """Raised when autonomous plant control, setpoint changes, or automatic commands are requested."""
    pass
