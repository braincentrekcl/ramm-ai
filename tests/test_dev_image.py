"""The dev image, built from .github/ci/dev.Dockerfile."""

import shutil
import subprocess

import acceptance
import acceptance_docker
import pytest


def dev_image_built() -> bool:
    """True when Docker runs and the dev image has been built before: building
    it from nothing takes minutes, which an ordinary test run should not."""
    if shutil.which("docker") is None:
        return False
    inspect = ["docker", "image", "inspect", acceptance_docker.IMAGE]
    return subprocess.run(inspect, capture_output=True, check=False).returncode == 0


@pytest.mark.skipif(not dev_image_built(), reason="needs Docker and the dev image")
def test_dev_image_has_every_agent_at_its_pin() -> None:
    acceptance_docker.build_image()
    for agent in acceptance.AGENT_PACKAGES:
        version = subprocess.run(
            ["docker", "run", "--rm", acceptance_docker.IMAGE, agent, "--version"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.splitlines()[0]
        assert acceptance.reported_version(version) == acceptance.pinned_version(agent)


@pytest.mark.skipif(not dev_image_built(), reason="needs Docker and the dev image")
def test_harness_runs_in_the_dev_image() -> None:
    acceptance_docker.build_image()
    # acceptance.py refuses to run unless the image sets this.
    marker = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            acceptance_docker.IMAGE,
            "printenv",
            "RAMM_AI_DEV_IMAGE",
        ],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert marker == "1"
