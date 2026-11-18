"""Checks that template/my-study.zip, which users download, matches the folder."""

import zipfile
from pathlib import Path

REBUILD = (
    "git archive --format=zip --prefix=my-study/ "
    "HEAD:template/my-study -o template/my-study.zip"
)


def zip_differences(archive: Path, folder: Path) -> list[str]:
    """Paths that are missing from, extra in, or different in the ZIP.

    Line endings are ignored: git on Windows can check the template out with
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


def test_template_zip_matches_the_folder(repo_root: Path) -> None:
    template = repo_root / "template"
    differences = zip_differences(template / "my-study.zip", template / "my-study")
    assert differences == [], (
        f"template/my-study.zip differs from the folder in {differences}; "
        f"commit the folder, then rebuild the ZIP with: {REBUILD}"
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
