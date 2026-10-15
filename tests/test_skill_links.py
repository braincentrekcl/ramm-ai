"""Every section link in the ramm skill points at a heading that exists."""

import re
from pathlib import Path

LINK = re.compile(r"\]\(([^)\s]*)#([^)\s]+)\)")


def slug(heading: str) -> str:
    """GitHub's anchor for a heading: lowercase, punctuation dropped, spaces to hyphens."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def anchors(markdown: str) -> set[str]:
    prose = re.sub(r"```.*?```", "", markdown, flags=re.DOTALL)
    return {slug(h) for h in re.findall(r"^#+ (.+)$", prose, flags=re.MULTILINE)}


def broken_links(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    broken = []
    for target, anchor in LINK.findall(text):
        target_path = (path.parent / target) if target else path
        if anchor not in anchors(target_path.read_text(encoding="utf-8")):
            broken.append(f"{target}#{anchor}")
    return broken


def test_skill_section_links_resolve(repo_root: Path) -> None:
    skill = repo_root / "skills" / "ramm"
    for path in (skill / "SKILL.md", skill / "references" / "script.md"):
        assert broken_links(path) == [], f"{path.name} has broken section links"


def test_broken_link_is_reported(tmp_path: Path) -> None:
    page = tmp_path / "page.md"
    page.write_text(
        "## Data access\n\nSee [Data access](#data-access) and [gone](#gone).\n"
    )
    assert broken_links(page) == ["#gone"]


def test_slug_matches_github() -> None:
    assert (
        slug("The maximal-then-simplify strategy (Barr et al., 2013)")
        == "the-maximal-then-simplify-strategy-barr-et-al-2013"
    )
