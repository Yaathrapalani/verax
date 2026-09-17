import pytest
from pathlib import Path

DOCKERFILE_BACKEND = Path("Dockerfile")
DOCKERFILE_FRONTEND = Path("frontend/Dockerfile")
DOCKER_COMPOSE_PATH = Path("docker-compose.yml")
ENV_EXAMPLE_PATH = Path(".env.example")


def test_configuration_files_exist():
    assert DOCKERFILE_BACKEND.exists()
    assert DOCKERFILE_FRONTEND.exists()
    assert DOCKER_COMPOSE_PATH.exists()
    assert ENV_EXAMPLE_PATH.exists()


def test_env_example_contents():
    content = ENV_EXAMPLE_PATH.read_text()
    assert "PORT=" in content
    assert "HOST=" in content
    assert "ENVIRONMENT=" in content
