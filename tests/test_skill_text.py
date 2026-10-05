"""Guards for behaviour-carrying rules in the skill text (spec sections 4-6)."""

import re
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


def section(skill: str, start: str, end: str) -> str:
    return skill.split(start, 1)[1].split(end, 1)[0]


def test_input_md_required(ramm_skill: str) -> None:
    a = section(ramm_skill, "## A.", "## B.")
    assert "inputs/input.md" in a
    assert "registered report" in a
    assert "Never write in `inputs/`" in a
    assert "keep real data out of the study folder" in a


def test_agent_never_opens_data(ramm_skill: str) -> None:
    c = section(ramm_skill, "## C.", "## D.")
    assert "Read the first 20 rows" not in ramm_skill
    assert "Open no other data file" in c
    assert "Never search inside data files" in c


def test_skill_expects_data_absent(ramm_skill: str) -> None:
    c = section(ramm_skill, "## C.", "## D.")
    assert "may not be in the folder when you write the script" in c


def test_skill_handles_non_csv_data_file(ramm_skill: str) -> None:
    c = section(ramm_skill, "## C.", "## D.")
    assert "readr::read_tsv()" in c and "readxl::read_excel()" in c


def test_skill_refuses_unprefixed_toy_file(ramm_skill: str) -> None:
    c = section(ramm_skill, "## C.", "## D.")
    assert "does not start with `toy_`, do not open it" in c


def test_data_file_item_in_checklist(ramm_skill: str) -> None:
    assert "### B.9 Data File" in ramm_skill


OUTPUT_CALL = re.compile(r'(write\.csv\([^,]+,\s*|ggsave\(|png\(|file\()"([^"]+)"')


def r_blocks(skill: str) -> list[str]:
    return re.findall(r"```r\n(.*?)```", skill, flags=re.DOTALL)


def test_outputs_written_under_outputs(ramm_skill_raw: str) -> None:
    literal_paths = [
        m.group(2)
        for block in r_blocks(ramm_skill_raw)
        for m in OUTPUT_CALL.finditer(block)
    ]
    assert literal_paths == [], (
        f'Output paths not built with file.path("outputs", ...): {literal_paths}'
    )


def test_script_never_prints_data_rows(ramm_skill: str, ramm_skill_raw: str) -> None:
    assert "first few rows" not in ramm_skill
    assert "Never print data rows" in ramm_skill
    for block in r_blocks(ramm_skill_raw):
        assert not re.search(r"\b(head|str|glimpse|View)\(dat\b", block)
        assert "print(dat)" not in block
