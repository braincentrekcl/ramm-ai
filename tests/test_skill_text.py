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


REPRODUCE_COMMANDS = [
    "/ramm:reproduce",
    "$ramm:reproduce",
    "/reproduce",
    "@reproduce",
]
EXPORT_COMMANDS = [
    "/export code/sessions/",
    "/share file code/sessions/",
    "`/export`",
    "~/.codex/sessions/",
]


def test_agent_never_runs_the_script(ramm_skill: str) -> None:
    g = section(ramm_skill, "## G.", "## H.")
    assert "Rscript --version" not in ramm_skill
    assert "You never run the script" in g
    assert "point them to the reproduce skill" in g


def test_outputs_read_only(ramm_skill: str) -> None:
    g = section(ramm_skill, "## G.", "## H.")
    assert "Never edit, create or delete a file in `outputs/`" in g


def test_reproduce_named_for_every_route(ramm_skill: str) -> None:
    g = section(ramm_skill, "## G.", "## H.")
    for command in REPRODUCE_COMMANDS:
        assert command in g


def test_session_record_requested(ramm_skill: str) -> None:
    g = section(ramm_skill, "## G.", "## H.")
    for command in EXPORT_COMMANDS:
        assert command in g


def test_no_old_codex_names(ramm_skill: str, reproduce_skill: str) -> None:
    for text in (ramm_skill, reproduce_skill):
        assert "$ramm input.md" not in text
        assert not re.search(r"\$reproduce\b", text)


def test_reproduce_uses_study_layout(reproduce_skill: str) -> None:
    for text in (
        "code/*_analysis.R",
        "inputs/input.md",
        "Rscript code/setup_environment.R",
        "docker build -f code/Dockerfile",
        "COPY code/ /analysis/code/",
        "code/Dockerfile.dockerignore",
        "Write nothing outside `code/`",
    ):
        assert text in reproduce_skill, text
    assert "#### File: `.dockerignore`" not in reproduce_skill


def test_confirmation_leads_straight_to_script(ramm_skill: str) -> None:
    section_b = section(ramm_skill, "## B.", "### B.1")
    assert "write the script (Section G) in the same turn" in section_b


def test_script_name_has_a_default(ramm_skill: str) -> None:
    g = section(ramm_skill, "## G.", "## H.")
    assert "unless the user asks for another name" in g
    assert "ask the user what to name it" not in g


def test_session_record_names_one_dated_command(ramm_skill: str) -> None:
    g = section(ramm_skill, "## G.", "## H.")
    assert "<date>" not in g
    assert "code/sessions/YYYY-MM-DD" in g
    assert "Give only the command for the agent you are running in" in g


BASE_PLOT = re.compile(r"^\s*(plot|hist|qqnorm|boxplot|barplot)\(", flags=re.MULTILINE)


def test_base_plots_drawn_into_output_files(ramm_skill_raw: str) -> None:
    for block in r_blocks(ramm_skill_raw):
        unsaved = re.sub(
            r"png\(file\.path\(\"outputs\".*?dev\.off\(\)", "", block, flags=re.DOTALL
        )
        assert not BASE_PLOT.search(unsaved), (
            "Base plot drawn outside a png() device: writes Rplots.pdf"
        )


def test_reproduce_step_names_one_command(ramm_skill: str) -> None:
    g5 = section(ramm_skill, "**Reproducible environment:**", "**Session record:**")
    assert "Give only the command for the agent you are running in" in g5
    assert "otherwise list them" not in g5


def test_changes_are_announced_and_refusals_respected(ramm_skill: str) -> None:
    g = section(ramm_skill, "## G.", "## H.")
    assert "the agent may not ask them to approve it" in g
    assert "do not make it another way" in g
    assert "Never present the script as ready while you know of a problem in it" in g


def test_reproduce_changes_announced_and_refusals_respected(
    reproduce_skill: str,
) -> None:
    assert "the agent may not ask them to approve it" in reproduce_skill
    assert "do not make it another way" in reproduce_skill
    assert (
        "Never present the files as ready while you know of a problem in them"
        in reproduce_skill
    )


def test_session_record_is_verbatim(ramm_skill: str) -> None:
    g6 = ramm_skill.split("**Session record:**", 1)[1]
    assert "Never write your own summary in its place" in g6


def test_agent_never_runs_r(ramm_skill: str) -> None:
    g = section(ramm_skill, "## G.", "## H.")
    assert "Do not run R in any form, not even a syntax check" in g
