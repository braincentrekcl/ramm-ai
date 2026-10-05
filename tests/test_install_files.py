"""Install files for each agent route (spec section 3)."""

from pathlib import Path

import tomllib
from conftest import read_json, read_jsonc

DATA_EXTENSIONS = ("csv", "tsv", "xlsx", "xls")


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


def test_gemini_extension_matches_plugin(repo_root: Path) -> None:
    extension = read_json(repo_root / "gemini-extension.json")
    plugin = read_json(repo_root / ".claude-plugin" / "plugin.json")
    assert extension["name"] == plugin["name"]
    assert extension["version"] == plugin["version"]
    assert extension["description"]


def test_gemini_commands_activate_each_skill(repo_root: Path) -> None:
    for file_name, skill in (
        ("ramm.toml", "ramm"),
        ("ramm-reproduce.toml", "reproduce"),
    ):
        command = tomllib.loads(
            (repo_root / "commands" / file_name).read_text(encoding="utf-8")
        )
        assert set(command) == {"description", "prompt"}
        assert f"`{skill}` skill" in command["prompt"]
        assert "{{args}}" in command["prompt"]


def test_opencode_template_rules(repo_root: Path) -> None:
    config = read_jsonc(repo_root / "opencode" / "opencode.jsonc")
    assert config["skills"] == ["/path/to/ramm-ai/skills"]
    assert "providers" not in config and "model" not in config
    rules = [(r["action"], r["resource"], r["effect"]) for r in config["permissions"]]
    expected = (
        [("shell", "*", "deny"), ("grep", "*", "deny")]
        + [("read", f"*.{ext}", "deny") for ext in DATA_EXTENSIONS]
        + [
            ("read", "*toy_*", "allow"),
            ("edit", "*", "deny"),
            ("edit", "code/*", "allow"),
        ]
    )
    assert rules == expected
