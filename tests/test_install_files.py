"""Install files for each agent route (spec section 3)."""

from fnmatch import fnmatchcase
from pathlib import Path

import pytest
from conftest import read_json, read_jsonc


def test_claude_marketplace_lists_plugin_at_repo_root(repo_root: Path) -> None:
    marketplace = read_json(repo_root / ".claude-plugin" / "marketplace.json")
    assert marketplace["name"] == "ramm-ai"
    assert marketplace["owner"]["name"]
    assert marketplace["plugins"] == [
        {
            "name": "ramm",
            "source": "./",
            "description": marketplace["plugins"][0]["description"],
        }
    ]
    plugin = read_json(repo_root / ".claude-plugin" / "plugin.json")
    assert marketplace["plugins"][0]["name"] == plugin["name"]


def test_codex_manifest_matches_claude_manifest(repo_root: Path) -> None:
    codex = read_json(repo_root / ".codex-plugin" / "plugin.json")
    claude = read_json(repo_root / ".claude-plugin" / "plugin.json")
    for key in ("name", "version", "description"):
        assert codex[key] == claude[key]


def test_codex_marketplace_points_at_repo_root(repo_root: Path) -> None:
    marketplace = read_json(repo_root / ".agents" / "plugins" / "marketplace.json")
    assert marketplace["name"] == "ramm-ai"
    entry = marketplace["plugins"][0]
    assert entry["name"] == "ramm"
    assert entry["source"] == {"source": "local", "path": "./"}
    assert entry["policy"]["installation"] == "AVAILABLE"


def decide(rules: list[dict], action: str, resource: str) -> str:
    """OpenCode applies the last matching rule; with none, its default allows."""
    effect = "allow"
    for rule in rules:
        if rule["action"] == action and fnmatchcase(resource, rule["resource"]):
            effect = rule["effect"]
    return effect


# OpenCode matches read and edit rules against the path relative to the study
# folder, even when the model asks for a full path (checked in 2.0.24).
# Paths outside the study folder are stopped by external_directory instead.


@pytest.fixture
def opencode_rules(repo_root: Path) -> list[dict]:
    config = read_jsonc(repo_root / "opencode" / "opencode.jsonc")
    assert config["skills"] == ["/path/to/ramm-ai/skills"]
    assert "providers" not in config and "model" not in config
    return config["permissions"]


@pytest.mark.parametrize(
    "path",
    [
        "inputs/input.md",
        "inputs/toy_data.csv",
        "outputs/analysis_log.txt",
        "outputs/brain_regions_analysis_log.txt",
        "outputs/results_comparisons.csv",
        "outputs/results_summary.md",
        "outputs/provenance.csv",
        "outputs/plot_emmeans.png",
        "code/analysis.R",
        "envs/Dockerfile",
    ],
)
def test_opencode_allows_reading(opencode_rules: list[dict], path: str) -> None:
    assert decide(opencode_rules, "read", path) == "allow"


@pytest.mark.parametrize(
    "path",
    [
        "inputs/data.csv",
        "inputs/notes.md",
        "inputs/data.rds",
        "inputs/toy_old/real_data.csv",
        "outputs/old/data.csv",
        "outputs/results_old/data.csv",
        "DATA.CSV",
        "data.xlsx",
        "data/barcode/x.csv",
        "notes/participants.json",
        "toy_project/real_data.csv",
        "archive/inputs/input.md",
        "pipeline_outputs/results_scores.csv",
        "old/code/data.csv",
    ],
)
def test_opencode_denies_reading_data(opencode_rules: list[dict], path: str) -> None:
    assert decide(opencode_rules, "read", path) == "deny"


@pytest.mark.parametrize(
    ("path", "effect"),
    [
        ("code/analysis.R", "allow"),
        ("envs/Dockerfile", "allow"),
        ("inputs/input.md", "deny"),
        ("outputs/results_summary.md", "deny"),
    ],
)
def test_opencode_edit_rules(
    opencode_rules: list[dict], path: str, effect: str
) -> None:
    assert decide(opencode_rules, "edit", path) == effect


@pytest.mark.parametrize(
    "action",
    [
        "shell",
        "grep",
        "execute",
        "subagent",
        "webfetch",
        "websearch",
        "external_directory",
    ],
)
def test_opencode_denies_other_tools(opencode_rules: list[dict], action: str) -> None:
    assert decide(opencode_rules, action, "anything") == "deny"
