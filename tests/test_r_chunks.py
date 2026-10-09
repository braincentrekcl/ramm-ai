"""Run the R chunks from the skill's script template (base R only)."""

import csv
import hashlib
import os
import re
import subprocess
import time
from pathlib import Path

import pytest
from conftest import extract_r_chunk, run_r


@pytest.fixture
def skill_text(repo_root: Path) -> str:
    return (repo_root / "skills" / "ramm" / "SKILL.md").read_text(encoding="utf-8")


def make_study(root: Path) -> Path:
    for folder in ("inputs", "code"):
        (root / folder).mkdir(parents=True)
    (root / "inputs" / "input.md").write_text(
        "# Study Design (required)\n", encoding="utf-8"
    )
    return root


def test_setup_chunk_stops_outside_study_folder(
    skill_text: str, tmp_path: Path
) -> None:
    result = run_r(extract_r_chunk(skill_text, "setup"), tmp_path)
    assert result.returncode != 0
    assert "Run this script from your study folder" in result.stderr


def test_setup_chunk_creates_outputs_and_log(skill_text: str, tmp_path: Path) -> None:
    study = make_study(tmp_path)
    code = (
        extract_r_chunk(skill_text, "setup")
        + 'cat("hello\\n")\nsink()\nclose(log_con)\n'
    )
    result = run_r(code, study)
    assert result.returncode == 0, result.stderr
    assert "hello" in (study / "outputs" / "analysis_log.txt").read_text(
        encoding="utf-8"
    )


DATA_HEADER = "subject_id,slide_id,section,drug_group,uci_g\n"


def run_checks(
    skill_text: str, study: Path, rows: str
) -> subprocess.CompletedProcess[str]:
    (study / "inputs" / "data.csv").write_text(DATA_HEADER + rows, encoding="utf-8")
    code = (
        'dat <- read.csv(file.path("inputs", "data.csv"))\n'
        + extract_r_chunk(skill_text, "data-checks")
        + 'cat("checks passed\\n")\n'
    )
    return run_r(code, study)


def balanced_rows() -> str:
    groups = ("vehicle", "drugA", "drugB", "drugC")
    return "".join(f"{g}_{i},1,1,{g},1.0\n" for g in groups for i in range(1, 13))


def test_data_checks_pass_on_matching_data(skill_text: str, tmp_path: Path) -> None:
    result = run_checks(skill_text, make_study(tmp_path), balanced_rows())
    assert result.returncode == 0, result.stderr
    assert "checks passed" in result.stdout


def test_data_checks_stop_on_missing_column(skill_text: str, tmp_path: Path) -> None:
    study = make_study(tmp_path)
    (study / "inputs" / "data.csv").write_text(
        "subject_id,drug_group\nA,vehicle\n", encoding="utf-8"
    )
    code = 'dat <- read.csv(file.path("inputs", "data.csv"))\n' + extract_r_chunk(
        skill_text, "data-checks"
    )
    result = run_r(code, study)
    assert result.returncode != 0
    assert "not in the data file: slide_id, section, uci_g" in result.stderr


def test_data_checks_stop_on_subject_in_two_groups(
    skill_text: str, tmp_path: Path
) -> None:
    rows = balanced_rows() + "vehicle_1,1,1,drugA,1.0\n"
    result = run_checks(skill_text, make_study(tmp_path), rows)
    assert result.returncode != 0
    assert "appear in more than one group: vehicle_1" in result.stderr


def test_data_checks_stop_on_group_size_mismatch(
    skill_text: str, tmp_path: Path
) -> None:
    rows = "".join(
        line + "\n"
        for line in balanced_rows().splitlines()
        if not line.startswith("drugC_12")
    )
    result = run_checks(skill_text, make_study(tmp_path), rows)
    assert result.returncode != 0
    assert "does not match inputs/input.md" in result.stderr


def test_data_checks_stop_on_unexpected_group(skill_text: str, tmp_path: Path) -> None:
    rows = balanced_rows() + "extra_1,1,1,drugE,1.0\n"
    result = run_checks(skill_text, make_study(tmp_path), rows)
    assert result.returncode != 0
    assert "groups that are not in inputs/input.md: drugE" in result.stderr


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def run_provenance(skill_text: str, study: Path) -> list[dict[str, str]]:
    (study / "code" / "analysis.R").write_text("# script\n", encoding="utf-8")
    (study / "inputs" / "data.csv").write_text("a\n1\n", encoding="utf-8")
    (study / "outputs").mkdir()
    old = study / "outputs" / "results_old.csv"
    old.write_text("stale\n", encoding="utf-8")
    past = time.time() - 3600
    os.utime(old, (past, past))
    code = (
        'run_started <- as.POSIXct(floor(as.numeric(Sys.time())), origin = "1970-01-01")\n'
        "required_packages <- character(0)\n"
        'writeLines("new", file.path("outputs", "results_new.csv"))\n'
        + extract_r_chunk(skill_text, "provenance")
    )
    result = run_r(code, study)
    assert result.returncode == 0, result.stderr
    with (study / "outputs" / "provenance.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        return list(csv.DictReader(handle))


def test_provenance_records_script_inputs_outputs(
    skill_text: str, tmp_path: Path
) -> None:
    study = make_study(tmp_path)
    rows = run_provenance(skill_text, study)
    files = {
        (r["type"], r["name"]): r["value"] for r in rows if r["type"] != "software"
    }
    assert files[("script", "code/analysis.R")] == md5(study / "code" / "analysis.R")
    assert files[("input", "inputs/input.md")] == md5(study / "inputs" / "input.md")
    assert files[("input", "inputs/data.csv")] == md5(study / "inputs" / "data.csv")
    assert files[("output", "outputs/results_new.csv")] == md5(
        study / "outputs" / "results_new.csv"
    )
    assert {r["name"] for r in rows if r["type"] == "software"} == {"R"}
    assert len({r["recorded_at"] for r in rows}) == 1


def test_provenance_skips_outputs_from_earlier_runs(
    skill_text: str, tmp_path: Path
) -> None:
    rows = run_provenance(skill_text, make_study(tmp_path))
    names = {r["name"] for r in rows}
    assert "outputs/results_old.csv" not in names
    assert "outputs/provenance.csv" not in names


def test_setup_chunk_accepts_named_input_file(skill_text: str, tmp_path: Path) -> None:
    for folder in ("inputs", "code"):
        (tmp_path / folder).mkdir()
    (tmp_path / "inputs" / "brain_regions.md").write_text(
        "# Study Design (required)\n", encoding="utf-8"
    )
    code = extract_r_chunk(skill_text, "setup") + "sink()\nclose(log_con)\n"
    result = run_r(code, tmp_path)
    assert result.returncode == 0, result.stderr


def test_messages_after_log_closed_do_not_break_provenance(
    skill_text: str, tmp_path: Path
) -> None:
    study = make_study(tmp_path)
    (study / "code" / "analysis.R").write_text("# script\n", encoding="utf-8")
    code = (
        extract_r_chunk(skill_text, "setup")
        + "old_contrasts <- options()\nrequired_packages <- character(0)\n"
        + extract_r_chunk(skill_text, "session-info")
        + 'message("after the log is closed")\n'
        + extract_r_chunk(skill_text, "provenance")
    )
    result = run_r(code, study)
    assert result.returncode == 0, result.stderr
    assert (study / "outputs" / "provenance.csv").is_file()


def test_provenance_stops_when_script_file_missing(
    skill_text: str, tmp_path: Path
) -> None:
    study = make_study(tmp_path)
    (study / "outputs").mkdir()
    code = (
        "run_started <- Sys.time()\nrequired_packages <- character(0)\n"
        + extract_r_chunk(skill_text, "provenance")
    )
    result = run_r(code, study)
    assert result.returncode != 0
    assert "script_file" in result.stderr


def test_predictor_guard_runs_on_an_lm(skill_text: str, tmp_path: Path) -> None:
    """Section 6c is kept for one-observation-per-individual lm() designs."""
    section_6 = skill_text.split("# --- 6. Model Diagnostics ---", 1)[1]
    guard = section_6.split("# 6c.", 1)[1].split("# 6d.", 1)[0]
    code = (
        "dat <- data.frame(y = rnorm(40), group = gl(4, 10))\n"
        "model <- lm(y ~ group, data = dat)\n"
        "# 6c." + guard + 'cat("guard ran:", n_fixed_params, "\\n")\n'
    )
    result = run_r(code, tmp_path)
    assert result.returncode == 0, result.stderr
    assert "guard ran: 4" in result.stdout


def test_lm_anova_is_type_three(skill_text: str, tmp_path: Path) -> None:
    """lm() gets Type III tests like lmer(), checked against the definition."""
    if run_r(
        'quit(status = !requireNamespace("car", quietly = TRUE))', tmp_path
    ).returncode:
        pytest.skip("the car package is not installed")
    section_7 = skill_text.split("### Section 7: Model Summary", 1)[1].split(
        "### Section 8", 1
    )[0]
    match = re.search(r"`(car::Anova\(model[^`]*\))`", section_7)
    assert match, "Section 7 gives no car::Anova() call for lm() designs"
    code = (
        'options(contrasts = c("contr.sum", "contr.poly"))\n'
        "set.seed(1)\n"
        "dat <- data.frame(a = factor(rep(c('x', 'y'), c(14, 6))),\n"
        "                  b = factor(rep(c('p', 'q', 'p', 'q'), c(10, 4, 2, 4))))\n"
        "dat$y <- rnorm(20) + (dat$a == 'y') + (dat$b == 'q')\n"
        "model <- lm(y ~ a * b, data = dat)\n"
        f"type_three <- {match.group(1)}\n"
        "# Type III by definition: drop the columns for 'a' from the model\n"
        "# matrix, keeping 'b' and 'a:b', and compare residual sums of squares.\n"
        "X <- model.matrix(model)\n"
        "a_term <- which(attr(terms(model), 'term.labels') == 'a')\n"
        "keep <- attr(X, 'assign') != a_term\n"
        "rss_full <- sum(resid(model)^2)\n"
        "rss_without_a <- sum(lm.fit(X[, keep], dat$y)$residuals^2)\n"
        "f_definition <- ((rss_without_a - rss_full) / sum(!keep)) /\n"
        "  (rss_full / df.residual(model))\n"
        'stopifnot(abs(type_three["a", "F value"] - f_definition) < 1e-8)\n'
        'cat("type three ok\\n")\n'
    )
    result = run_r(code, tmp_path)
    assert result.returncode == 0, result.stderr
    assert "type three ok" in result.stdout
