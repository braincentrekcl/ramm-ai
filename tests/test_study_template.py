"""The study template and the skill's input format stay in step (spec 4.1)."""

import re
from pathlib import Path


def headings(markdown: str) -> list[str]:
    return re.findall(r"^# (.+)$", markdown, flags=re.MULTILINE)


def test_skill_section_i_matches_template(repo_root: Path) -> None:
    skill = (repo_root / "skills" / "ramm" / "SKILL.md").read_text(encoding="utf-8")
    section_i = skill.split("## I. Input File Format", 1)[1]
    block = re.search(r"```markdown\n(.*?)```", section_i, flags=re.DOTALL).group(1)
    template = (repo_root / "template" / "my-study" / "inputs" / "input.md").read_text(
        encoding="utf-8"
    )
    assert headings(block) == headings(template)
