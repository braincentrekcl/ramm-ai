"""Checks on the R code examples in the skill, which agents copy into scripts."""

import re
from pathlib import Path

import pytest

OUTPUT_CALL = re.compile(r'(write\.csv\([^,]+,\s*|ggsave\(|png\(|file\()"([^"]+)"')
BASE_PLOT = re.compile(r"^\s*(plot|hist|qqnorm|boxplot|barplot)\(", flags=re.MULTILINE)


@pytest.fixture
def ramm_skill_raw(repo_root: Path) -> str:
    return (repo_root / "skills" / "ramm" / "SKILL.md").read_text(encoding="utf-8")


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


def test_examples_never_print_data_rows(ramm_skill_raw: str) -> None:
    for block in r_blocks(ramm_skill_raw):
        assert not re.search(r"\b(head|str|glimpse|View)\(dat\b", block)
        assert "print(dat)" not in block


def test_base_plots_drawn_into_output_files(ramm_skill_raw: str) -> None:
    for block in r_blocks(ramm_skill_raw):
        unsaved = re.sub(
            r"png\(file\.path\(\"outputs\".*?dev\.off\(\)", "", block, flags=re.DOTALL
        )
        assert not BASE_PLOT.search(unsaved), (
            "Base plot drawn outside a png() device: writes Rplots.pdf"
        )
