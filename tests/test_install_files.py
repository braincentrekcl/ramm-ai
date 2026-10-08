"""Install files for each agent route (spec section 3)."""

from pathlib import Path

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
            ("read", "*inputs/*", "deny"),
            ("read", "*inputs/input.md", "allow"),
            ("read", "*inputs/toy_*", "allow"),
            ("edit", "*", "deny"),
            ("edit", "code/*", "allow"),
            ("edit", "envs/*", "allow"),
            ("execute", "*", "deny"),
            ("subagent", "*", "deny"),
            ("webfetch", "*", "deny"),
            ("websearch", "*", "deny"),
        ]
    )
    assert rules == expected
