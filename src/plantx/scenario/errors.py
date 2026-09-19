"""Canonical errors for Stage 9 Scenario Intelligence."""

class ScenarioError(Exception):
    """Base exception for Stage 9 Scenario errors."""
    pass


class TemporalScenarioViolation(ScenarioError):
    """Raised when scenario parameter or calculation consumes future observations t > T."""
    pass


class ScenarioSourceMutation(ScenarioError):
    """Raised if raw source evidence or dataset is mutated during scenario execution."""
    pass


class UnsupportedPerturbationError(ScenarioError):
    """Raised when a scenario parameter perturbation exceeds allowed prototype scenario bounds."""
    pass


class ScenarioStage10BoundaryViolation(ScenarioError):
    """Raised if an attempt is made to execute Stage 10 economic decision optimization or autonomous control from Stage 9."""
    pass
