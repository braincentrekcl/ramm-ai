"""Guards for behaviour-carrying rules in the skill text (spec sections 4-6)."""

from pathlib import Path

import pytest


def flat(text: str) -> str:
    """Collapse whitespace, so phrases match across wrapped lines."""
    return " ".join(text.split())


@pytest.fixture
def ramm_skill_raw(repo_root: Path) -> str:
    return (repo_root / "skills" / "ramm" / "SKILL.md").read_text(encoding="utf-8")


@pytest.fixture
def ramm_skill(ramm_skill_raw: str) -> str:
    return flat(ramm_skill_raw)


@pytest.fixture
def reproduce_skill(repo_root: Path) -> str:
    return flat(
        (repo_root / "skills" / "reproduce" / "SKILL.md").read_text(encoding="utf-8")
    )


def test_scope_rule_comes_before_section_a(ramm_skill: str) -> None:
    assert ramm_skill.index("## Scope") < ramm_skill.index("## A.")
    assert "only handles the analysis" in ramm_skill


def test_simpler_model_flagged_in_confirmation(ramm_skill: str) -> None:
    section_b = ramm_skill.split("## B.", 1)[1].split("### B.1", 1)[0]
    assert "no replicates, nesting or random effects" in section_b
