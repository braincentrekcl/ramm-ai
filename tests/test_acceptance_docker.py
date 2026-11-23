"""The command that runs an acceptance batch in the dev image."""

from pathlib import Path

import acceptance_docker
import pytest


def mounts(command: list[str]) -> list[str]:
    return [command[i + 1] for i, arg in enumerate(command) if arg == "--mount"]


def env_names(command: list[str]) -> list[str]:
    return [command[i + 1] for i, arg in enumerate(command) if arg == "--env"]


def test_claude_gets_only_its_own_credential_by_name(tmp_path: Path) -> None:
    env = {"CLAUDE_CODE_OAUTH_TOKEN": "secret-x", "COPILOT_GITHUB_TOKEN": "secret-y"}
    command = acceptance_docker.run_command("claude", tmp_path, ["open-field"], env)
    passed = env_names(command)
    assert "CLAUDE_CODE_OAUTH_TOKEN" in passed
    assert not any("COPILOT" in name for name in passed)
    assert not any("secret" in arg for arg in command)


def test_only_the_output_folder_is_writable(tmp_path: Path) -> None:
    env = {"CLAUDE_CODE_OAUTH_TOKEN": "x"}
    command = acceptance_docker.run_command("claude", tmp_path, ["open-field"], env)
    writable = [m for m in mounts(command) if not m.endswith(",readonly")]
    assert writable == [f"type=bind,source={tmp_path},target=/out"]
    assert not any(".codex" in m for m in mounts(command))


def test_codex_gets_its_login_read_only_and_no_token(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".codex" / "auth.json").write_text("login")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    command = acceptance_docker.run_command("codex", tmp_path, ["open-field"], {})
    codex = [m for m in mounts(command) if ".codex" in m]
    assert len(codex) == 1 and codex[0].endswith(",readonly")
    assert not any(name.endswith("TOKEN") for name in env_names(command))


def test_missing_credential_stops_before_docker(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="CLAUDE_CODE_OAUTH_TOKEN"):
        acceptance_docker.run_command("claude", tmp_path, ["open-field"], {})


def test_harness_writes_to_the_mounted_output_folder(tmp_path: Path) -> None:
    env = {"COPILOT_GITHUB_TOKEN": "x"}
    command = acceptance_docker.run_command(
        "copilot", tmp_path, ["open-field", "--runs", "3"], env
    )
    harness = command[command.index("tests/acceptance.py") :]
    assert harness == [
        "tests/acceptance.py",
        "copilot",
        "open-field",
        "--runs",
        "3",
        "--out",
        "/out",
    ]


def test_codex_without_a_login_stops_before_docker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    with pytest.raises(SystemExit, match="auth.json"):
        acceptance_docker.run_command("codex", tmp_path, ["open-field"], {})
