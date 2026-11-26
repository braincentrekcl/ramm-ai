"""version.py bumps RAMM-AI's version in every file that holds it."""

import importlib.util
import shutil
from pathlib import Path
from types import ModuleType

import pytest


def load_version_module(repo_root: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("version", repo_root / "version.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def version_module(repo_root: Path) -> ModuleType:
    return load_version_module(repo_root)


@pytest.fixture
def copy_root(repo_root: Path, version_module: ModuleType, tmp_path: Path) -> Path:
    """A copy of only the files that hold the version."""
    for relative_path, _, _ in version_module.PLACES:
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(repo_root / relative_path, target)
    return tmp_path


def test_bump_changes_every_place(version_module: ModuleType, copy_root: Path) -> None:
    old_version = version_module.current_version(copy_root)
    version_module.bump(copy_root, "9.8.7")
    assert version_module.current_version(copy_root) == "9.8.7"
    for relative_path, template, expected_count in version_module.PLACES:
        text = (copy_root / relative_path).read_text(encoding="utf-8")
        assert text.count(template.format(version="9.8.7")) == expected_count
        assert template.format(version=old_version) not in text


def test_bump_keeps_each_file_line_endings(
    version_module: ModuleType, copy_root: Path
) -> None:
    for relative_path in ("VERSION", ".claude-plugin/plugin.json"):
        path = copy_root / relative_path
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    version_module.bump(copy_root, "9.8.7")
    assert (copy_root / "VERSION").read_bytes() == b"9.8.7\r\n"
    assert b"\r\n" in (copy_root / ".claude-plugin" / "plugin.json").read_bytes()
    assert b"\r" not in (copy_root / ".codex-plugin" / "plugin.json").read_bytes()


def test_bump_refuses_a_malformed_version(
    version_module: ModuleType, copy_root: Path
) -> None:
    with pytest.raises(ValueError, match="not a version"):
        version_module.bump(copy_root, "v0.3")


def test_bump_writes_nothing_when_a_place_lacks_the_version(
    version_module: ModuleType, copy_root: Path
) -> None:
    old_version = version_module.current_version(copy_root)
    renv = copy_root / "skills" / "reproduce" / "references" / "renv.md"
    renv.write_text("no version here\n", encoding="utf-8")
    with pytest.raises(ValueError, match="renv.md"):
        version_module.bump(copy_root, "9.8.7")
    assert version_module.current_version(copy_root) == old_version
