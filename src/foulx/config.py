from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectConfig:
    """Minimal configuration placeholder for the M0 foundation."""

    project_name: str = "FOUL-X"
    human_approval_required: bool = True
