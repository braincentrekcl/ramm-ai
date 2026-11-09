"""Checks for the helpers in the headless acceptance harness."""

import json
import re
from pathlib import Path

import acceptance
import pytest


def test_changed_files_lists_added_removed_and_modified() -> None:
    before = {"a": "1", "b": "2", "c": "3"}
    after = {"a": "1", "b": "9", "d": "4"}
    assert acceptance.changed_files(before, after) == ["b", "c", "d"]


def test_changed_files_is_empty_when_nothing_changed() -> None:
    assert acceptance.changed_files({"a": "1"}, {"a": "1"}) == []


def test_runs_r_finds_rscript_and_r_calls() -> None:
    assert acceptance.runs_r("cd study && Rscript code/analysis.R")
    assert acceptance.runs_r("/bin/zsh -lc 'R -e \"1+1\"'")


def test_runs_r_ignores_other_commands() -> None:
    assert not acceptance.runs_r("ls -R code")
    assert not acceptance.runs_r("cat code/analysis.R")


def test_runs_r_ignores_a_script_written_with_a_heredoc() -> None:
    command = "cat > code/analysis.R <<'EOF'\n#   Rscript code/analysis.R\nEOF"
    assert not acceptance.runs_r(command)
    assert acceptance.runs_r(command + "\nRscript code/analysis.R")


def test_runs_r_ignores_a_heredoc_quoted_by_a_shell_wrapper() -> None:
    # Codex wraps commands in zsh -lc '...', which quotes 'EOF' as '"'EOF'.
    command = (
        "/bin/zsh -lc 'cat > code/analysis.R <<'\"'EOF'\n"
        "#   Rscript code/analysis.R\nEOF\n'"
    )
    assert not acceptance.runs_r(command)


def test_leaked_rows_finds_a_data_row() -> None:
    rows = ['"M01","WT",94.4', '"M01","WT",104.4']
    assert acceptance.leaked_rows('1\t"M01","WT",104.4\n', rows)


def test_leaked_rows_ignores_the_header_and_other_text() -> None:
    rows = ['"M01","WT",94.4']
    assert not acceptance.leaked_rows('"mouse_id","genotype","binding"', rows)


@pytest.mark.parametrize(
    "text",
    [
        "inputs/data.csv",
        "/Users/me/study/inputs/data.xlsx",
        "head -1 inputs/raw_counts.tsv | cut -d, -f2",
    ],
)
def test_names_input_data_finds_a_data_file(text: str) -> None:
    assert acceptance.names_input_data(text)


@pytest.mark.parametrize(
    "text",
    [
        "inputs/input.md",
        "/Users/me/study/inputs/toy_data.csv",
        "ls -1 inputs/",
        "rg --files -g '!inputs/*.csv' .",
        "cat > code/analysis.R <<'EOF'\n# reads inputs/data.csv\nEOF\n",
    ],
)
def test_names_input_data_ignores_allowed_files_listings_and_heredocs(
    text: str,
) -> None:
    assert not acceptance.names_input_data(text)


def test_tool_paths_collects_path_arguments() -> None:
    arguments = {"file_path": "inputs/data.csv", "limit": 1, "pattern": "WT"}
    assert acceptance.tool_paths(arguments) == ["inputs/data.csv"]
    assert acceptance.tool_paths({"filePath": "a.R", "paths": ["b", "c"]}) == [
        "a.R",
        "b",
        "c",
    ]


def test_tool_paths_accepts_arguments_given_as_text() -> None:
    # Copilot passes some tools' arguments as one string, not named fields.
    assert acceptance.tool_paths("*** Begin Patch\n") == []


def test_extract_formula_skips_comments() -> None:
    script = (
        "# model <- lmer(y ~ a + (1 | s), data = dat)\n"
        "model <- lmer(\n  y ~ a * b +\n    (1 | s),\n  data = dat\n)\n"
    )
    assert acceptance.extract_formula(script) == "y ~ a * b + (1 | s)"


def test_extract_formula_returns_none_without_a_model() -> None:
    assert acceptance.extract_formula("library(lme4)\n") is None


def test_same_formula_ignores_term_order_and_spacing() -> None:
    assert acceptance.same_formula("y ~ a + (1 | s) + (1 | t)", "y~a+(1|t)+(1|s)")


def test_same_formula_tells_a_random_slope_apart() -> None:
    assert not acceptance.same_formula("y ~ a + (1 | s)", "y ~ a + (1 + a | s)")


AUTORADIOGRAPHY = acceptance.REFERENCES["autoradiography"]
COMPARISONS_HEADER = "contrast,region,estimate,SE,df\n"


def write_comparisons(folder: Path, rows: str) -> None:
    (folder / "results_comparisons.csv").write_text(COMPARISONS_HEADER + rows)


def test_reference_matched_finds_the_contrast_row(tmp_path: Path) -> None:
    write_comparisons(tmp_path, '"het − WT","striatum",-14.5576,5.8557,42.17\n')
    assert acceptance.reference_matched(tmp_path, AUTORADIOGRAPHY)


@pytest.mark.parametrize(
    "row",
    [
        '"het - WT","striatum",-12.10,5.86,42.17\n',  # another estimate
        '"het - WT","striatum",14.56,5.86,42.17\n',  # sign reversed
        '"het - WT","striatum",-14.56,6.10,36.40\n',  # another df method
        '"hom - WT","striatum",-14.56,5.86,42.17\n',  # another contrast
        '"het - WT","sensory cortex",-14.56,5.86,42.17\n',  # another region
    ],
)
def test_reference_matched_rejects_other_rows(tmp_path: Path, row: str) -> None:
    write_comparisons(tmp_path, row)
    assert not acceptance.reference_matched(tmp_path, AUTORADIOGRAPHY)


def test_reference_matched_ignores_the_numbers_in_another_table(
    tmp_path: Path,
) -> None:
    # The fixed effects can hold the reference numbers under another label.
    (tmp_path / "results_fixed_effects.csv").write_text(
        'term,estimate,SE,df\n"genotypehet",-14.56,5.86,42.17\n'
    )
    write_comparisons(tmp_path, '"het - WT","striatum",-14.56,6.10,36.40\n')
    assert not acceptance.reference_matched(tmp_path, AUTORADIOGRAPHY)


def test_error_excerpt_starts_at_the_error() -> None:
    output = "Loading\nfine\nError in f(): bad\n  more\n"
    assert acceptance.error_excerpt(output) == "Error in f(): bad\n  more"


def test_error_excerpt_falls_back_to_the_last_lines() -> None:
    output = "\n".join(str(i) for i in range(50))
    assert acceptance.error_excerpt(output, max_lines=2) == "48\n49"


def test_claude_items_keeps_content_dicts() -> None:
    event = {"message": {"content": [{"type": "text"}, "plain"]}}
    assert acceptance.claude_items(event) == [{"type": "text"}]


def test_claude_items_ignores_events_without_content() -> None:
    assert acceptance.claude_items({"message": "a status line"}) == []
    assert acceptance.claude_items({"type": "result"}) == []


def test_result_text_joins_text_parts_and_strings() -> None:
    assert acceptance.result_text([{"text": "a"}, "b", {"type": "image"}]) == "a\nb\n"
    assert acceptance.result_text("plain") == "plain"


def test_skill_read_rule_anchors_at_the_filesystem_root() -> None:
    rule = acceptance.skill_read_rule(Path("/tmp/run/plugin"))
    assert rule == "Read(//tmp/run/plugin/skills/**)"


def test_skill_read_rule_refuses_a_relative_path() -> None:
    with pytest.raises(ValueError, match="absolute"):
        acceptance.skill_read_rule(Path("plugin"))


COPILOT_EVENTS = [
    {"type": "assistant.message", "data": {"content": "", "model": "gpt-x"}},
    {
        "type": "tool.execution_start",
        "data": {"toolCallId": "a", "toolName": "bash", "arguments": {"command": "ls"}},
    },
    {
        "type": "tool.execution_complete",
        "data": {"toolCallId": "a", "success": True, "result": {"content": "x.R"}},
    },
    {
        "type": "tool.execution_start",
        "data": {"toolCallId": "b", "toolName": "bash", "arguments": {"command": "R"}},
    },
    {
        "type": "tool.execution_complete",
        "data": {"toolCallId": "b", "success": False, "error": {"code": "denied"}},
    },
    {"type": "assistant.message", "data": {"content": "Done.", "model": "gpt-x"}},
    {"type": "result", "sessionId": "s1", "exitCode": 0},
]


def test_parse_copilot_reads_commands_denials_reply_and_session() -> None:
    turn = acceptance.Turn(tag="", prompt="p")
    stdout = "\n".join(json.dumps(e) for e in COPILOT_EVENTS)
    session, models = acceptance.parse_copilot(stdout, turn)
    assert (session, models) == ("s1", {"gpt-x"})
    assert turn.commands == ["ls", "R"]
    assert turn.denied == ['{"command": "R"}']
    assert (turn.reply, turn.tool_output) == ("Done.", "x.R")


def test_parse_copilot_records_the_paths_its_tools_read() -> None:
    view = {
        "type": "tool.execution_start",
        "data": {"toolCallId": "v", "toolName": "view", "arguments": {"path": "x.md"}},
    }
    turn = acceptance.Turn(tag="", prompt="p")
    stdout = "\n".join(json.dumps(e) for e in [view, COPILOT_EVENTS[-1]])
    acceptance.parse_copilot(stdout, turn)
    assert turn.paths == ["x.md"]


def test_parse_copilot_returns_no_session_without_a_result() -> None:
    turn = acceptance.Turn(tag="", prompt="p")
    session, _ = acceptance.parse_copilot(json.dumps(COPILOT_EVENTS[0]), turn)
    assert session is None


def test_runs_r_ignores_a_lookup_of_where_r_is() -> None:
    assert not acceptance.runs_r("command -v Rscript || true")
    assert not acceptance.runs_r("which R")
    assert acceptance.runs_r("which R && Rscript --version")


def test_reuse_plugin_is_false_without_a_copy(tmp_path: Path) -> None:
    assert not acceptance.reuse_plugin(tmp_path / "plugin", "abc1234")


def test_reuse_plugin_accepts_a_copy_of_this_commit(tmp_path: Path) -> None:
    plugin = tmp_path / "plugin"
    plugin.mkdir()
    (plugin / acceptance.PLUGIN_STAMP).write_text("abc1234\n")
    assert acceptance.reuse_plugin(plugin, "abc1234")


@pytest.mark.parametrize("stamp", ["0d074db\n", None])
def test_reuse_plugin_refuses_a_copy_of_another_commit(
    tmp_path: Path, stamp: str | None
) -> None:
    plugin = tmp_path / "plugin"
    plugin.mkdir()
    if stamp:
        (plugin / acceptance.PLUGIN_STAMP).write_text(stamp)
    with pytest.raises(SystemExit, match="use a new --out folder"):
        acceptance.reuse_plugin(plugin, "abc1234")


RAMM_SCRIPT = """# ============================================================
# Mixed-Effects Model Analysis
# ============================================================
required_packages <- c("readr", "lme4", "lmerTest", "emmeans", "ggplot2",
                        "broom.mixed", "dplyr", "tidyr")
dat <- readr::read_csv(file.path("inputs", "data.csv"))
# all_fits <- allFit(model)
# boot_fits <- bootMer(model, FUN = fixef, nsim = 1000)
model <- lmer(log(y) ~ age * marker + (1 | mouse_id), data = dat)
"""


def test_beyond_ramm_is_empty_for_ramm_script() -> None:
    assert acceptance.beyond_ramm(RAMM_SCRIPT) == []


def test_beyond_ramm_finds_other_packages_and_calls() -> None:
    script = RAMM_SCRIPT + (
        'library(nlme)\nlibrary("boot")\nfit <- optim(start, negloglik)\n'
        "ci <- lme4::bootMer(model, FUN = fixef, nsim = 1000)\n"
    )
    assert acceptance.beyond_ramm(script) == [
        "boot",
        "nlme",
        "bootMer()",
        "optim()",
    ]


def test_beyond_ramm_is_empty_for_the_template(repo_root: Path) -> None:
    script = (repo_root / "skills" / "ramm" / "references" / "script.md").read_text(
        encoding="utf-8"
    )
    code = "\n".join(re.findall(r"```r\n(.*?)```", script, flags=re.DOTALL))
    assert acceptance.beyond_ramm(code) == []


def test_beyond_ramm_still_finds_a_package_loaded_by_name() -> None:
    script = RAMM_SCRIPT + 'library("nlme", character.only = TRUE)\n'
    assert acceptance.beyond_ramm(script) == ["nlme"]


def test_beyond_ramm_finds_packages_in_the_required_list() -> None:
    script = RAMM_SCRIPT.replace('"tidyr")', '"tidyr", "glmmTMB")')
    assert acceptance.beyond_ramm(script) == ["glmmTMB"]


def test_header_discloses_a_method_in_the_opening_comments() -> None:
    script = (
        "# Beyond RAMM-AI’s supported methods: parametric bootstrap\n" + RAMM_SCRIPT
    )
    assert acceptance.header_discloses(script)


def test_header_discloses_ignores_the_heading_after_the_header() -> None:
    script = RAMM_SCRIPT + "# Beyond RAMM-AI's supported methods\n"
    assert not acceptance.header_discloses(script)
    assert not acceptance.header_discloses(RAMM_SCRIPT)


def test_uncommented_drops_whole_line_and_trailing_comments() -> None:
    script = "# header\nx <- 1  # bootMer(m) later\n\ny <- 2\n"
    assert acceptance.uncommented(script) == "x <- 1  \ny <- 2"


def test_uncommented_keeps_a_hash_inside_a_string() -> None:
    script = "label <- \"group # 1\" # note\nq <- 'it\\'s # here'\n"
    assert acceptance.uncommented(script) == (
        "label <- \"group # 1\" \nq <- 'it\\'s # here'"
    )


def test_beyond_ramm_ignores_a_call_in_a_trailing_comment() -> None:
    script = RAMM_SCRIPT + "fit <- model  # bootMer(model) would be slower\n"
    assert acceptance.beyond_ramm(script) == []


def test_ramm_packages_come_from_the_skill() -> None:
    packages = acceptance.ramm_packages()
    assert {"lme4", "lmerTest", "emmeans", "readxl", "broom", "car"} <= packages
    assert "nlme" not in packages


def test_beyond_ramm_allows_grid_but_not_splines() -> None:
    script = RAMM_SCRIPT + "gap <- grid::unit(2, 'mm')\nbasis <- splines::ns(age, 3)\n"
    assert acceptance.beyond_ramm(script) == ["splines"]
