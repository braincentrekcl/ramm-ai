"""Checks for the helpers in the headless acceptance harness."""

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


def test_leaked_rows_finds_a_data_row() -> None:
    rows = ['"M01","WT",94.4', '"M01","WT",104.4']
    assert acceptance.leaked_rows('1\t"M01","WT",104.4\n', rows)


def test_leaked_rows_ignores_the_header_and_other_text() -> None:
    rows = ['"M01","WT",94.4']
    assert not acceptance.leaked_rows('"mouse_id","genotype","binding"', rows)


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


def test_reference_matched_finds_estimate_and_se(tmp_path: Path) -> None:
    (tmp_path / "results_comparisons.csv").write_text(
        'contrast,estimate,SE\n"het - WT",-14.5576,5.8557\n'
    )
    assert acceptance.reference_matched(tmp_path, -14.56, 5.86)


def test_reference_matched_is_false_for_other_numbers(tmp_path: Path) -> None:
    (tmp_path / "results_comparisons.csv").write_text(
        'contrast,estimate,SE\n"het - WT",-12.10,5.86\n'
    )
    assert not acceptance.reference_matched(tmp_path, -14.56, 5.86)


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
