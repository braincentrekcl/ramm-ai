"""Checks that each ZIP users download matches its folder."""

import zipfile
from pathlib import Path

import pytest

ZIPPED_FOLDERS = [
    "template/my-study",
    "examples/demo-autoradiography",
    "examples/demo-open-field",
    "examples/demo-paired-markers",
]


def zip_differences(archive: Path, folder: Path) -> list[str]:
    """Paths that are missing from, extra in, or different in the ZIP.

    Line endings are ignored: git on Windows can check the folder out with
    CRLF while the ZIP keeps LF.
    """
    with zipfile.ZipFile(archive) as zf:
        zipped = {
            name.removeprefix(f"{folder.name}/"): zf.read(name).replace(b"\r\n", b"\n")
            for name in zf.namelist()
            if not name.endswith("/")
        }
    files = {
        str(p.relative_to(folder)): p.read_bytes().replace(b"\r\n", b"\n")
        for p in folder.rglob("*")
        if p.is_file()
    }
    return sorted(
        path for path in set(zipped) | set(files) if zipped.get(path) != files.get(path)
    )


@pytest.mark.parametrize("folder", ZIPPED_FOLDERS)
def test_zip_matches_the_folder(repo_root: Path, folder: str) -> None:
    differences = zip_differences(repo_root / f"{folder}.zip", repo_root / folder)
    rebuild = (
        f"git archive --format=zip --prefix={Path(folder).name}/ "
        f"HEAD:{folder} -o {folder}.zip"
    )
    assert differences == [], (
        f"{folder}.zip differs from the folder in {differences}; "
        f"commit the folder, then rebuild the ZIP with: {rebuild}"
    )


def test_zip_differences_finds_a_changed_file(tmp_path: Path) -> None:
    folder = tmp_path / "my-study"
    (folder / "inputs").mkdir(parents=True)
    (folder / "inputs" / "input.md").write_text("new template\n")
    archive = tmp_path / "my-study.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("my-study/inputs/input.md", "old template\n")
        zf.writestr("my-study/notes.txt", "only in the ZIP\n")
    assert zip_differences(archive, folder) == ["inputs/input.md", "notes.txt"]


def test_zip_differences_ignores_line_endings(tmp_path: Path) -> None:
    folder = tmp_path / "my-study"
    (folder / "inputs").mkdir(parents=True)
    (folder / "inputs" / "input.md").write_bytes(b"# Study\r\nline\r\n")
    archive = tmp_path / "my-study.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("my-study/inputs/input.md", "# Study\nline\n")
    assert zip_differences(archive, folder) == []
