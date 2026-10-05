"""The study template and the skill's input format stay in step (spec 4.1)."""

import re
from pathlib import Path

REQUIRED = ["Study Design", "Column Mappings", "Post-Hoc Comparisons", "Data File"]
OPTIONAL = ["QC Rules", "Preferences", "Reproducible Environment", "Toy Data"]


def headings(markdown: str) -> list[str]:
    return re.findall(r"^# (.+)$", markdown, flags=re.MULTILINE)


def test_template_layout(repo_root: Path) -> None:
    study = repo_root / "template" / "my-study"
    assert (study / "inputs" / "input.md").is_file()
    assert (study / "code" / "sessions").is_dir()
    assert (study / "outputs").is_dir()


def test_template_headings_marked(repo_root: Path) -> None:
    text = (repo_root / "template" / "my-study" / "inputs" / "input.md").read_text(
        encoding="utf-8"
    )
    expected = [f"{h} (required)" for h in REQUIRED] + [
        f"{h} (optional)" for h in OPTIONAL
    ]
    assert headings(text) == expected
    assert "add headings of your own" in " ".join(text.split())


def test_skill_section_i_matches_template(repo_root: Path) -> None:
    skill = (repo_root / "skills" / "ramm" / "SKILL.md").read_text(encoding="utf-8")
    section_i = skill.split("## I. Input File Format", 1)[1]
    block = re.search(r"```markdown\n(.*?)```", section_i, flags=re.DOTALL).group(1)
    template = (repo_root / "template" / "my-study" / "inputs" / "input.md").read_text(
        encoding="utf-8"
    )
    assert headings(block) == headings(template)


def test_root_input_file_removed(repo_root: Path) -> None:
    assert not (repo_root / "input.MD").exists()
