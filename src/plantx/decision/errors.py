"""Canonical error types for Stage 10 Decision Intelligence."""

class DecisionError(Exception):
    """Base exception for Stage 10 Decision errors."""
    pass


class TemporalDecisionViolation(DecisionError):
    """Raised when decision evaluation consumes future evidence t > T."""
    pass


class DecisionSourceMutation(DecisionError):
    """Raised if raw source evidence or dataset is mutated during decision evaluation."""
    pass


class AutonomousControlViolationError(DecisionError):
    """Raised if an attempt is made to execute autonomous plant control, setpoint changes, or automatic cleaning commands."""
    pass
