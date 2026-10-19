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
    return (repo_root / "skills" / "ramm" / "references" / "script.md").read_text(
        encoding="utf-8"
    )


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


def test_data_checks_warn_on_fewer_individuals_than_planned(
    skill_text: str, tmp_path: Path
) -> None:
    rows = "".join(
        line + "\n"
        for line in balanced_rows().splitlines()
        if not line.startswith("drugC_12")
    )
    result = run_checks(skill_text, make_study(tmp_path), rows)
    assert result.returncode == 0, result.stderr
    assert "checks passed" in result.stdout
    assert "drugC: planned 12, in data 11" in result.stderr
    assert "Fewer individuals than planned in: drugC" in result.stderr


def test_data_checks_stop_on_more_individuals_than_planned(
    skill_text: str, tmp_path: Path
) -> None:
    rows = balanced_rows() + "drugC_13,1,1,drugC,1.0\n"
    result = run_checks(skill_text, make_study(tmp_path), rows)
    assert result.returncode != 0
    assert "more individuals in the data than inputs/input.md plans" in result.stderr


def test_data_checks_stop_on_unexpected_group(skill_text: str, tmp_path: Path) -> None:
    rows = balanced_rows() + "extra_1,1,1,drugE,1.0\n"
    result = run_checks(skill_text, make_study(tmp_path), rows)
    assert result.returncode != 0
    assert "groups that are not in inputs/input.md: drugE" in result.stderr


# The chunk's example plans 4 slides per individual and 3 sections per slide.
GROUPING_DATA = """
dat <- expand.grid(subject_id = paste0("s", 1:3), slide_num = 1:4, section = 1:3,
                   stringsAsFactors = FALSE)
dat$slide_uid <- paste(dat$subject_id, dat$slide_num, sep = "_")
dat$section_uid <- paste(dat$slide_uid, dat$section, sep = "_")
"""


def run_grouping_checks(
    skill_text: str, tmp_path: Path, change: str = ""
) -> subprocess.CompletedProcess[str]:
    code = (
        GROUPING_DATA
        + change
        + extract_r_chunk(skill_text, "grouping-checks")
        + 'cat("checks passed\\n")\n'
    )
    return run_r(code, tmp_path)


def test_grouping_checks_pass_on_planned_design(
    skill_text: str, tmp_path: Path
) -> None:
    result = run_grouping_checks(skill_text, tmp_path)
    assert result.returncode == 0, result.stderr
    assert "checks passed" in result.stdout


def test_grouping_checks_stop_when_labels_split_a_unit(
    skill_text: str, tmp_path: Path
) -> None:
    # Two regions measured on the same slide, wrongly put into the slide label.
    split = (
        'dat$region <- ifelse(dat$section == 1, "a", "b")\n'
        'dat$slide_uid <- paste(dat$subject_id, dat$region, dat$slide_num, sep = "_")\n'
    )
    result = run_grouping_checks(skill_text, tmp_path, split)
    assert result.returncode != 0
    assert "up to 8 slides per individual where inputs/input.md plans 4" in (
        result.stderr
    )


def test_grouping_checks_stop_when_labels_are_shared_across_units(
    skill_text: str, tmp_path: Path
) -> None:
    # Slide numbers restart in every individual and were used without the individual.
    shared = "dat$slide_uid <- as.character(dat$slide_num)\n"
    result = run_grouping_checks(skill_text, tmp_path, shared)
    assert result.returncode != 0
    assert "'slide_uid' labels appear in more than one 'subject_id'" in result.stderr


def test_grouping_checks_report_lost_units_without_stopping(
    skill_text: str, tmp_path: Path
) -> None:
    lost = 'dat <- dat[dat$slide_uid != "s1_4", ]\n'
    result = run_grouping_checks(skill_text, tmp_path, lost)
    assert result.returncode == 0, result.stderr
    assert "1 of 3 units have fewer slides per individual than planned" in (
        result.stderr
    )


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


def test_lm_anova_is_type_three(skill_text: str, tmp_path: Path) -> None:
    """lm() gets Type III tests like lmer(), checked against the definition."""
    if run_r(
        'quit(status = !requireNamespace("car", quietly = TRUE))', tmp_path
    ).returncode:
        pytest.skip("the car package is not installed")
    section_7 = skill_text.split("## Section 7: Model Summary", 1)[1].split(
        "## Section 8", 1
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


def test_strip_plot_keeps_rows_when_individuals_get_every_condition(
    skill_text: str, tmp_path: Path
) -> None:
    """In a crossover each individual is in every condition; no row is copied."""
    if run_r(
        'quit(status = !requireNamespace("dplyr", quietly = TRUE))', tmp_path
    ).returncode:
        pytest.skip("the dplyr package is not installed")
    strip_code = skill_text.split("# One strip per individual,", 1)[1].split(
        "# Violin width", 1
    )[0]
    code = (
        "dat <- expand.grid(subject_id = paste0('m', 1:4), rep = 1:3,\n"
        "                   drug_group = c('vehicle', 'drug'))\n"
        "dat$drug_group <- factor(dat$drug_group, levels = c('vehicle', 'drug'))\n"
        "dat$uci_g <- seq_len(nrow(dat))\n"
        "# One strip per individual," + strip_code + "\n"
        "stopifnot(nrow(plot_dat) == nrow(dat))\n"
        'cat("rows kept\\n")\n'
    )
    result = run_r(code, tmp_path)
    assert result.returncode == 0, result.stderr
    assert "rows kept" in result.stdout


SLOPE_PACKAGES = ("lme4", "lmerTest", "emmeans", "dplyr")


def run_slopes(
    skill_text: str, study: Path, individuals: str
) -> subprocess.CompletedProcess[str]:
    """Simulate a genotype x dose study, fit it, and run the slope chunks.

    `individuals` is R code for a data frame with one row per individual:
    subject_id, genotype and dose. WT slope is 2, het slope 0.5.
    """
    missing = run_r(
        "pkgs <- c(" + ", ".join(f'"{p}"' for p in SLOPE_PACKAGES) + ")\n"
        "quit(status = !all(vapply(pkgs, requireNamespace, logical(1), quietly = TRUE)))",
        study,
    ).returncode
    if missing:
        pytest.skip("lme4, lmerTest, emmeans or dplyr is not installed")
    code = (
        "suppressPackageStartupMessages({library(lme4); library(lmerTest); library(emmeans)})\n"
        'options(contrasts = c("contr.sum", "contr.poly"))\n'
        "set.seed(1)\n"
        f"ids <- {individuals}\n"
        "ids$offset <- rnorm(nrow(ids))\n"
        "dat <- ids[rep(seq_len(nrow(ids)), each = 4), ]\n"
        'dat$genotype <- factor(dat$genotype, levels = c("WT", "het"))\n'
        'dat$uci_g <- 50 + ifelse(dat$genotype == "WT", 2, 0.5) * dat$dose +\n'
        "  dat$offset + rnorm(nrow(dat), sd = 0.5)\n"
        + extract_r_chunk(skill_text, "centring")
        + "model <- lmer(uci_g ~ genotype * dose_centred + (1 | subject_id), data = dat)\n"
        + extract_r_chunk(skill_text, "slopes")
        + extract_r_chunk(skill_text, "slopes-export")
    )
    (study / "outputs").mkdir()
    return run_r(code, study)


def test_slopes_recover_the_simulated_trends(skill_text: str, tmp_path: Path) -> None:
    result = run_slopes(
        skill_text,
        tmp_path,
        "data.frame(subject_id = paste0('m', 1:24),\n"
        "  genotype = rep(c('WT', 'het'), each = 12),\n"
        "  dose = rep(seq(0, 10, length.out = 12), 2))",
    )
    assert result.returncode == 0, result.stderr
    with (tmp_path / "outputs" / "results_slopes.csv").open(encoding="utf-8") as f:
        rows = {row["genotype"]: row for row in csv.DictReader(f)}
    assert list(rows["WT"]) == [
        "genotype",
        "slope",
        "standard_error",
        "degrees_of_freedom",
        "ci95_lower",
        "ci95_upper",
        "t_value",
        "p_value_adjusted",
    ]
    assert abs(float(rows["WT"]["slope"]) - 2) < 0.3
    assert abs(float(rows["het"]["slope"]) - 0.5) < 0.3
    # Satterthwaite df: limited by the 24 individuals, not the 96 measurements.
    assert 2 <= float(rows["WT"]["degrees_of_freedom"]) < 24


def test_slopes_stop_when_too_few_individuals(skill_text: str, tmp_path: Path) -> None:
    result = run_slopes(
        skill_text,
        tmp_path,
        "data.frame(subject_id = paste0('m', 1:5),\n"
        "  genotype = c('WT', 'WT', 'WT', 'het', 'het'),\n"
        "  dose = c(0, 5, 10, 2, 8))",
    )
    assert result.returncode != 0
    assert "fewer than 2 degrees of freedom" in result.stderr
    assert not (tmp_path / "outputs" / "results_slopes.csv").exists()
