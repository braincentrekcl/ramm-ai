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


SLOPE_PACKAGES = ("lme4", "lmerTest", "emmeans", "dplyr", "ggplot2")


def run_slopes(
    skill_text: str, study: Path, individuals: str, after: str = ""
) -> subprocess.CompletedProcess[str]:
    """Simulate a genotype x dose study, fit it, and run the slope chunks.

    `individuals` is R code for a data frame with one row per individual:
    subject_id, genotype and dose. WT slope is 2, het slope 0.5.
    `after` is R code run once the chunks have run.
    """
    missing = run_r(
        "pkgs <- c(" + ", ".join(f'"{p}"' for p in SLOPE_PACKAGES) + ")\n"
        "quit(status = !all(vapply(pkgs, requireNamespace, logical(1), quietly = TRUE)))",
        study,
    ).returncode
    if missing:
        pytest.skip("lme4, lmerTest, emmeans, dplyr or ggplot2 is not installed")
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
        + after
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
        after="r <- slope_results\n"
        "# 95% intervals: estimate +/- t(0.975, df) x SE, with no adjustment.\n"
        "stopifnot(isTRUE(all.equal(r$ci95_lower,\n"
        "  r$slope - qt(0.975, r$degrees_of_freedom) * r$standard_error)))\n"
        "# Holm-adjusted p-values, compared as ratios: tiny p-values would pass\n"
        "# an absolute comparison whatever they were.\n"
        "raw_p <- 2 * pt(-abs(r$t_value), r$degrees_of_freedom)\n"
        'stopifnot(max(abs(r$p_value / p.adjust(raw_p, "holm") - 1)) < 1e-6)\n'
        'cat("intervals and tests ok\\n")\n',
    )
    assert result.returncode == 0, result.stderr
    assert "intervals and tests ok" in result.stdout
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
        "p_value",
        "p_value_adjustment",
    ]
    assert rows["WT"]["p_value_adjustment"] == "holm"
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


@pytest.mark.parametrize("centre", ["mean(dat$dose, na.rm = TRUE)", "0", "8"])
def test_slope_plot_shows_the_fitted_line_on_the_original_doses(
    skill_text: str, tmp_path: Path, centre: str
) -> None:
    """Whatever centre input.md chooses, the plot shows the doses as given."""
    default = "dose_centre <- mean(dat$dose, na.rm = TRUE)"
    assert default in skill_text
    skill_text = skill_text.replace(default, f"dose_centre <- {centre}")
    result = run_slopes(
        skill_text,
        tmp_path,
        "data.frame(subject_id = paste0('m', 1:24),\n"
        "  genotype = rep(c('WT', 'het'), each = 12),\n"
        "  dose = rep(seq(0, 10, length.out = 12), 2))",
        after="suppressPackageStartupMessages(library(ggplot2))\n"
        + extract_r_chunk(skill_text, "slope-plot")
        + "stopifnot(all.equal(range(line_df$dose), range(dat$dose)))\n"
        "stopifnot(all(line_df$lower.CL < line_df$emmean),\n"
        "          all(line_df$emmean < line_df$upper.CL))\n"
        "stopifnot(setequal(unique(line_df$genotype), levels(dat$genotype)))\n"
        "invisible(ggplot_build(estimate_plot))\n"
        'cat("plot ok\\n")\n',
    )
    assert result.returncode == 0, result.stderr
    assert "plot ok" in result.stdout


@pytest.mark.parametrize("centre", ["mean(dat$dose, na.rm = TRUE)", "0", "8"])
def test_group_difference_matches_the_f_test_at_the_centre(
    skill_text: str, tmp_path: Path, centre: str
) -> None:
    """A two-level difference has the F-test's p-value, whatever the centre."""
    default = "dose_centre <- mean(dat$dose, na.rm = TRUE)"
    assert default in skill_text
    skill_text = skill_text.replace(default, f"dose_centre <- {centre}")
    at_call = re.search(r"`(emmeans\(model, ~ genotype, at = [^`]*\))`", skill_text)
    assert at_call, "Section 8 gives no emmeans() call at the predictor's centre"
    export = skill_text.split("contrast_results <- as.data.frame", 1)[1].split(
        "write.csv(contrast_results", 1
    )[0]
    result = run_slopes(
        skill_text,
        tmp_path,
        "data.frame(subject_id = paste0('m', 1:24),\n"
        "  genotype = rep(c('WT', 'het'), each = 12),\n"
        "  dose = rep(seq(0, 10, length.out = 12), 2))",
        after=f"emm <- {at_call.group(1)}\n"
        'contrast_output <- contrast(emm, method = "revpairwise", adjust = "none")\n'
        "contrast_results <- as.data.frame" + export + "\n"
        'f_test <- anova(model, type = 3, ddf = "Satterthwaite")["genotype", ]\n'
        "# One difference: t squared is F, so the tests are the same test.\n"
        "# (all.equal() would compare tiny p-values on an absolute scale.)\n"
        'stopifnot(abs(contrast_results$t_value^2 / f_test[["F value"]] - 1) < 1e-6)\n'
        'stopifnot(identical(contrast_results$p_value_adjustment, "none"))\n'
        'cat("matches f test\\n")\n',
    )
    assert result.returncode == 0, result.stderr
    assert "matches f test" in result.stdout


def test_slopes_ignore_a_missing_dose(skill_text: str, tmp_path: Path) -> None:
    """One individual without a dose leaves the centre and the model intact."""
    result = run_slopes(
        skill_text,
        tmp_path,
        "data.frame(subject_id = paste0('m', 1:24),\n"
        "  genotype = rep(c('WT', 'het'), each = 12),\n"
        "  dose = c(NA, seq(0, 10, length.out = 12)[-1],\n"
        "           seq(0, 10, length.out = 12)))",
        after="stopifnot(is.finite(dose_centre))\n"
        "stopifnot(nobs(model) == sum(!is.na(dat$dose)))\n"
        'cat("missing dose ok\\n")\n',
    )
    assert result.returncode == 0, result.stderr
    assert "missing dose ok" in result.stdout


def test_one_slope_without_interaction_uses_the_original_column(
    skill_text: str, tmp_path: Path
) -> None:
    """Without an interaction nothing is centred, so the slope call names dose."""
    if run_r(
        'pkgs <- c("lme4", "lmerTest", "emmeans")\n'
        "quit(status = !all(vapply(pkgs, requireNamespace, logical(1), quietly = TRUE)))",
        tmp_path,
    ).returncode:
        pytest.skip("lme4, lmerTest or emmeans is not installed")
    bullet = re.search(
        r"- With no interaction, one slope for everyone: `([^`]*)`", skill_text
    )
    assert bullet, "Section 8 gives no slope call for a model without interaction"
    code = (
        "suppressPackageStartupMessages({library(lme4); library(lmerTest); library(emmeans)})\n"
        "set.seed(1)\n"
        "dat <- data.frame(subject_id = rep(paste0('m', 1:12), each = 4),\n"
        "                  dose = rep(seq(0, 10, length.out = 12), each = 4))\n"
        "dat$uci_g <- 50 + 2 * dat$dose + rep(rnorm(12), each = 4) +\n"
        "  rnorm(48, sd = 0.5)\n"
        "model <- lmer(uci_g ~ dose + (1 | subject_id), data = dat)\n"
        'emm_options(lmer.df = "satterthwaite")\n'
        f"slopes <- {bullet.group(1)}\n"
        "stopifnot(abs(summary(slopes)$dose.trend - 2) < 0.3)\n"
        'cat("one slope ok\\n")\n'
    )
    result = run_r(code, tmp_path)
    assert result.returncode == 0, result.stderr
    assert "one slope ok" in result.stdout


def run_continuous_check(
    skill_text: str, tmp_path: Path, dose: str
) -> subprocess.CompletedProcess[str]:
    """Run the continuous-column check on a data frame whose dose is `dose`."""
    code = (
        f"dat <- data.frame(subject_id = c('m1', 'm2', 'm3'), dose = {dose})\n"
        + extract_r_chunk(skill_text, "continuous-check")
        + 'cat("dose is", class(dat$dose), paste(dat$dose, collapse = " "), "\\n")\n'
    )
    return run_r(code, tmp_path)


def test_continuous_check_keeps_numbers(skill_text: str, tmp_path: Path) -> None:
    result = run_continuous_check(skill_text, tmp_path, "c(0, 2.5, 5)")
    assert result.returncode == 0, result.stderr
    assert "dose is numeric 0 2.5 5" in result.stdout
    assert "converted" not in result.stderr


def test_continuous_check_converts_numbers_read_as_text(
    skill_text: str, tmp_path: Path
) -> None:
    result = run_continuous_check(skill_text, tmp_path, "c(' 2.5', '5 ', '')")
    assert result.returncode == 0, result.stderr
    assert "dose is numeric 2.5 5 NA" in result.stdout
    assert "converted to numbers" in result.stderr


def test_continuous_check_stops_on_text(skill_text: str, tmp_path: Path) -> None:
    result = run_continuous_check(skill_text, tmp_path, "c('2.5', 'zz9', 'n/a')")
    assert result.returncode != 0
    assert "2 filled-in rows are not numbers" in result.stderr
    # The message counts the rows; it never prints the data values.
    assert "zz9" not in result.stderr
