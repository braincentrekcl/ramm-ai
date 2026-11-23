"""Run tests/acceptance.py in the dev image, on the pinned agent versions.

Builds .github/ci/dev.Dockerfile on the CI image (Docker's cache makes this
quick when nothing changed), then runs the harness in it with the repository
read-only, the output folder writable, and only the credential the agent needs.

Usage (from the repository root), with the same arguments as acceptance.py:
    python3 tests/acceptance_docker.py claude open-field --runs 3 --out <folder>

The credential comes from this script's environment, wherever you keep it:
CLAUDE_CODE_OAUTH_TOKEN (from `claude setup-token`) for Claude Code,
COPILOT_GITHUB_TOKEN for Copilot. Codex uses your ~/.codex/auth.json login;
OpenCode's free model needs none.
"""

import argparse
import json
import os
import subprocess
from collections.abc import Mapping
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
# The name .github/ci/dev.Dockerfile builds on.
CI_IMAGE = "ramm-ai-ci"
IMAGE = "ramm-ai-dev"
# The one variable each agent signs in with inside the container.
CREDENTIALS = {"claude": "CLAUDE_CODE_OAUTH_TOKEN", "copilot": "COPILOT_GITHUB_TOKEN"}


def agent_packages() -> str:
    """The pinned packages as npm install arguments, for the image's build."""
    pins = json.loads((REPO_ROOT / "tests" / "agent-versions.json").read_text())
    return " ".join(f"{package}@{version}" for package, version in pins.items())


def build_image() -> None:
    """Build the CI image, then the dev image on it; quick when nothing changed,
    as Docker caches both."""
    ci = ["docker", "build", "-f", ".github/ci/Dockerfile", "-t", CI_IMAGE]
    dev = ["docker", "build", "-f", ".github/ci/dev.Dockerfile", "-t", IMAGE]
    dev += ["--build-arg", f"AGENT_PACKAGES={agent_packages()}"]
    for command in (ci, dev):
        subprocess.run(command + [".github/ci"], cwd=REPO_ROOT, check=True)


def run_command(
    agent: str, out: Path, harness_args: list[str], env: Mapping[str, str]
) -> list[str]:
    """The docker run command for a batch; stops if the agent's credential is
    not set. The credential goes in by name, so its value is never on a command
    line."""
    command = ["docker", "run", "--rm"]
    if hasattr(os, "getuid"):
        # Output files then belong to the user (macOS and Linux).
        command += ["--user", f"{os.getuid()}:{os.getgid()}"]
    command += ["--mount", f"type=bind,source={REPO_ROOT},target=/repo,readonly"]
    command += ["--mount", f"type=bind,source={out},target=/out"]
    if agent == "codex":
        login = Path.home() / ".codex" / "auth.json"
        if not login.is_file():
            raise SystemExit(f"Log in to Codex first: {login} does not exist.")
        target = "/home/dev/.codex/auth.json"
        command += ["--mount", f"type=bind,source={login},target={target},readonly"]
    name = CREDENTIALS.get(agent)
    if name:
        if not env.get(name):
            raise SystemExit(f"Set {name} before running a {agent} batch.")
        command += ["--env", name]
    # The mounted repository belongs to another user inside the container.
    for setting in ("COUNT=1", "KEY_0=safe.directory", "VALUE_0=/repo"):
        command += ["--env", f"GIT_CONFIG_{setting}"]
    command += ["--workdir", "/repo", IMAGE]
    command += ["uv", "run", "--no-project", "python", "tests/acceptance.py"]
    return command + [agent, *harness_args, "--out", "/out"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("agent", choices=["claude", "codex", "copilot", "opencode"])
    parser.add_argument("--out", type=Path, required=True)
    args, harness_args = parser.parse_known_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    command = run_command(args.agent, out, harness_args, os.environ)
    build_image()
    raise SystemExit(subprocess.run(command, check=False).returncode)


if __name__ == "__main__":
    main()
