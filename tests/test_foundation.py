from foulx import __version__
from foulx.config import ProjectConfig


def test_package_version_exists():
    assert __version__ == "0.1.0"


def test_human_approval_is_required_by_default():
    assert ProjectConfig().human_approval_required is True
