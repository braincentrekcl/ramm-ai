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


STUDY = "/home/user/my-study"


@pytest.fixture
def opencode_rules(repo_root: Path) -> list[dict]:
    config = read_jsonc(repo_root / "opencode" / "opencode.jsonc")
    assert config["skills"] == ["/path/to/ramm-ai/skills"]
    assert "providers" not in config and "model" not in config
    return config["permissions"]


@pytest.mark.parametrize(
    "path",
    [
        f"{STUDY}/inputs/input.md",
        f"{STUDY}/inputs/toy_data.csv",
        "inputs/toy_data.csv",
        f"{STUDY}/outputs/analysis_log.txt",
        f"{STUDY}/outputs/results_comparisons.csv",
        f"{STUDY}/outputs/results_summary.md",
        f"{STUDY}/outputs/provenance.csv",
        f"{STUDY}/outputs/plot_emmeans.png",
        f"{STUDY}/outputs/brain_regions_analysis_log.txt",
        f"{STUDY}/code/analysis.R",
    ],
)
def test_opencode_allows_reading(opencode_rules: list[dict], path: str) -> None:
    assert decide(opencode_rules, "read", path) == "allow"


@pytest.mark.parametrize(
    "path",
    [
        f"{STUDY}/inputs/data.csv",
        "inputs/data.csv",
        f"{STUDY}/inputs/notes.md",
        f"{STUDY}/inputs/data.rds",
        f"{STUDY}/inputs/data.txt",
        "/home/user/toy_project/real_data.csv",
        "/home/user/elsewhere/data.xlsx",
        "/home/user/elsewhere/data.txt",
        "/home/user/elsewhere/data.sav",
        "/home/user/elsewhere/data.parquet",
        "/home/user/elsewhere/data.RData",
        "/home/user/elsewhere/DATA.CSV",
        "/home/user/elsewhere/data.XLSX",
        "/home/user/elsewhere/data.xlsm",
        "/home/user/elsewhere/data.Rdata",
        "/home/user/elsewhere/data.csv.gz",
        f"{STUDY}/inputs/toy_old/real_data.csv",
        "/home/user/other-project/outputs/participant_data.xlsx",
        "/home/user/pipeline_outputs/subject_scores.csv",
        f"{STUDY}/outputs/old/data.csv",
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
    "action", ["shell", "grep", "execute", "subagent", "webfetch", "websearch"]
)
def test_opencode_denies_other_tools(opencode_rules: list[dict], action: str) -> None:
    assert decide(opencode_rules, action, "anything") == "deny"
