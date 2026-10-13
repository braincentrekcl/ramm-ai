"""Shared helpers for RAMM-AI repository checks."""

import json
import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonc(path: Path) -> dict:
    """Parse JSONC whose comments are whole lines starting with //."""
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if not line.lstrip().startswith("//")
    ]
    return json.loads("\n".join(lines))


def extract_r_chunk(skill_text: str, name: str) -> str:
    """Return the ```r block that follows the marker <!-- chunk: name -->."""
    pattern = rf"<!-- chunk: {re.escape(name)} -->\s*```r\n(.*?)```"
    match = re.search(pattern, skill_text, flags=re.DOTALL)
    if match is None:
        raise AssertionError(f"No R chunk marked '{name}' in the skill text")
    return match.group(1)


def run_r(code: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    script = cwd / "_chunk_test.R"
    script.write_text(code, encoding="utf-8")
    return subprocess.run(
        ["Rscript", "--vanilla", str(script)],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
