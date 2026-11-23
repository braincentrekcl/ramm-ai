"""The agent versions CI checks and the acceptance harness runs."""

import json
import re
from pathlib import Path

import acceptance


def test_every_agent_is_pinned_to_an_exact_version(repo_root: Path) -> None:
    pins = json.loads((repo_root / "tests" / "agent-versions.json").read_text())
    assert set(pins) == set(acceptance.AGENT_PACKAGES.values())
    assert all(re.fullmatch(r"\d+\.\d+\.\d+", version) for version in pins.values())
