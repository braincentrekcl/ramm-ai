"""Run the data preparation checks that every prepare.R starts with."""

import subprocess
from pathlib import Path

import pytest
from conftest import extract_r_chunk, run_r


@pytest.fixture
def prepare_text(repo_root: Path) -> str:
    return (repo_root / "skills" / "ramm" / "references" / "prepare.md").read_text(
        encoding="utf-8"
    )


def run_checks(
    prepare_text: str, folder: Path, code: str
) -> subprocess.CompletedProcess[str]:
    return run_r(extract_r_chunk(prepare_text, "prepare-checks") + code, folder)


def test_record_step_prints_and_keeps_the_step(
    prepare_text: str, tmp_path: Path
) -> None:
    result = run_checks(
        prepare_text,
        tmp_path,
        'record_step("Read a.csv: 3 rows")\ncat(length(preparation_steps), "\\n")\n',
    )
    assert result.returncode == 0, result.stderr
    assert "Read a.csv: 3 rows" in result.stdout
    assert result.stdout.rstrip().endswith("1")


def test_files_found_passes_with_files(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(
        prepare_text,
        tmp_path,
        'check_files_found("inputs/raw/a.csv", "every .csv in inputs/raw/")\n',
    )
    assert result.returncode == 0, result.stderr


def test_files_found_stops_when_none_match(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(
        prepare_text,
        tmp_path,
        'check_files_found(character(0), "every .csv in inputs/raw/")\n',
    )
    assert result.returncode != 0
    assert "No files" in result.stderr
    assert "every .csv in inputs/raw/" in result.stderr


def test_columns_pass_when_present(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(
        prepare_text,
        tmp_path,
        'check_columns(data.frame(id = 1, score = 2), c("id", "score"), "b.csv")\n',
    )
    assert result.returncode == 0, result.stderr


def test_columns_stop_names_file(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(
        prepare_text,
        tmp_path,
        'check_columns(data.frame(id = 1), c("id", "score", "age"), "b.csv")\n',
    )
    assert result.returncode != 0
    assert "b.csv" in result.stderr
    assert "score, age" in result.stderr


def test_column_count_passes(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(
        prepare_text,
        tmp_path,
        'check_column_count(data.frame(a = 1, b = 2, c = 3), 3, "c.csv")\n',
    )
    assert result.returncode == 0, result.stderr


def test_column_count_stops(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(
        prepare_text,
        tmp_path,
        'check_column_count(data.frame(a = 1, b = 2, c = 3), 4, "c.csv")\n',
    )
    assert result.returncode != 0
    assert "3 columns" in result.stderr
    assert "4" in result.stderr


def test_rows_pass_when_equal(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(prepare_text, tmp_path, 'check_rows(12, 12, "Stacking")\n')
    assert result.returncode == 0, result.stderr


def test_rows_stop_when_different(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(prepare_text, tmp_path, 'check_rows(10, 12, "Stacking")\n')
    assert result.returncode != 0
    assert "Stacking" in result.stderr
    assert "12" in result.stderr
    assert "10" in result.stderr


def test_id_change_passes_without_merging(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(
        prepare_text,
        tmp_path,
        'ids <- c("m1", "m2", "m1")\ncheck_id_change(ids, toupper(ids), "d.xlsx")\n',
    )
    assert result.returncode == 0, result.stderr


def test_id_change_stops_on_case_merge(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(
        prepare_text,
        tmp_path,
        'ids <- c("m1", "M1", "m2")\ncheck_id_change(ids, toupper(ids), "d.xlsx")\n',
    )
    assert result.returncode != 0
    assert "m1 and M1" in result.stderr
    assert "d.xlsx" in result.stderr


def test_id_change_stops_on_padding_merge(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(
        prepare_text,
        tmp_path,
        'check_id_change(c("M1", "M01"), c("M01", "M01"), "d.xlsx")\n',
    )
    assert result.returncode != 0
    assert "M1 and M01" in result.stderr


def test_unique_ids_pass(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(
        prepare_text, tmp_path, 'check_unique_ids(c("A", "B"), "d.xlsx")\n'
    )
    assert result.returncode == 0, result.stderr


def test_unique_ids_stop_on_repeats(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(
        prepare_text, tmp_path, 'check_unique_ids(c("A", "B", "A"), "d.xlsx")\n'
    )
    assert result.returncode != 0
    assert "more than once" in result.stderr
    assert ": A" in result.stderr


def test_unique_ids_stop_on_missing_ids(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(
        prepare_text, tmp_path, 'check_unique_ids(c("A", "", NA), "d.xlsx")\n'
    )
    assert result.returncode != 0
    assert "2 rows" in result.stderr
    assert "no ID" in result.stderr


def test_join_passes_and_reports_extra_ids(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(
        prepare_text,
        tmp_path,
        'check_join(c("A", "B"), c("A", "B", "C"), "demographics.xlsx")\n',
    )
    assert result.returncode == 0, result.stderr
    assert "C" in result.stderr
    assert "demographics.xlsx" in result.stderr


def test_join_stops_listing_unmatched(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(
        prepare_text,
        tmp_path,
        'check_join(c("A", "B", "D"), c("A", "B"), "demographics.xlsx")\n',
    )
    assert result.returncode != 0
    assert ": D" in result.stderr
    assert "demographics.xlsx" in result.stderr


def test_join_compares_ids_as_text(prepare_text: str, tmp_path: Path) -> None:
    matched = run_checks(
        prepare_text, tmp_path, 'check_join(c(7, 8), c("7", "8"), "d.xlsx")\n'
    )
    assert matched.returncode == 0, matched.stderr
    padded = run_checks(prepare_text, tmp_path, 'check_join("007", 7, "d.xlsx")\n')
    assert padded.returncode != 0
    assert "007" in padded.stderr


def test_join_stops_on_missing_ids(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(
        prepare_text, tmp_path, 'check_join(c("A", NA), c("A"), "d.xlsx")\n'
    )
    assert result.returncode != 0
    assert "1 row" in result.stderr
    assert "no ID" in result.stderr


def test_log_missing_counts_per_column(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(
        prepare_text,
        tmp_path,
        'log_missing(data.frame(a = c(1, NA, NA), b = c(1, 2, 3)), "a.csv")\n',
    )
    assert result.returncode == 0, result.stderr
    assert "a: 2" in result.stdout
    assert "b:" not in result.stdout


def test_log_missing_says_none(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(
        prepare_text, tmp_path, 'log_missing(data.frame(a = 1), "a.csv")\n'
    )
    assert result.returncode == 0, result.stderr
    assert "No missing values in a.csv" in result.stdout


def test_join_matches_large_whole_number_ids(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(
        prepare_text, tmp_path, 'check_join(100000, "100000", "d.xlsx")\n'
    )
    assert result.returncode == 0, result.stderr


def test_id_change_stops_when_a_change_blanks_ids(
    prepare_text: str, tmp_path: Path
) -> None:
    result = run_checks(
        prepare_text,
        tmp_path,
        'check_id_change(c("M1", "M2"), c(NA, "M02"), "d.xlsx")\n',
    )
    assert result.returncode != 0
    assert "M1" in result.stderr
    assert "d.xlsx" in result.stderr


def test_ids_present_stops_on_blank_ids(prepare_text: str, tmp_path: Path) -> None:
    result = run_checks(
        prepare_text, tmp_path, 'check_ids_present(c("A", NA), "data.csv")\n'
    )
    assert result.returncode != 0
    assert "1 row in data.csv has no ID" in result.stderr


def test_dates_pass_when_every_filled_cell_is_a_date(
    prepare_text: str, tmp_path: Path
) -> None:
    result = run_checks(
        prepare_text,
        tmp_path,
        'check_dates(c("45231", NA), as.Date(c("2023-11-01", NA)), "dob", "d.xlsx", 2)\n',
    )
    assert result.returncode == 0, result.stderr


def test_dates_stop_when_a_filled_cell_is_not_a_date(
    prepare_text: str, tmp_path: Path
) -> None:
    result = run_checks(
        prepare_text,
        tmp_path,
        'check_dates(c("45231", "unknown", "45232"), '
        'as.Date(c("2023-11-01", NA, "2023-11-02")), "dob", "d.xlsx", 4)\n',
    )
    assert result.returncode != 0
    assert "dob" in result.stderr
    assert "d.xlsx" in result.stderr
    assert "row 5" in result.stderr
    assert "unknown" not in result.stderr


def read_and_check(
    prepare_text: str, folder: Path, lines: str, skip: int = 0
) -> subprocess.CompletedProcess[str]:
    (folder / "S01.csv").write_text(lines, encoding="utf-8")
    return run_checks(
        prepare_text,
        folder,
        f'table <- readr::read_csv("S01.csv", skip = {skip}, na = "",\n'
        '  col_types = readr::cols(.default = "c"))\n'
        f'check_read(table, "S01.csv", skipped_lines = {skip})\n',
    )


def test_read_stops_on_a_row_with_too_few_fields(
    prepare_text: str, tmp_path: Path
) -> None:
    result = read_and_check(prepare_text, tmp_path, "subject_id,score\nS01\nS02,4\n")
    assert result.returncode != 0
    assert "Line 2 of S01.csv" in result.stderr


def test_read_stops_on_a_row_with_too_many_fields(
    prepare_text: str, tmp_path: Path
) -> None:
    result = read_and_check(
        prepare_text, tmp_path, "export\nrun 3\nsubject_id,score\nS01,3,9\n", skip=2
    )
    assert result.returncode != 0
    assert "Line 4 of S01.csv" in result.stderr
    assert "3,9" not in result.stderr


def test_read_passes_an_empty_field(prepare_text: str, tmp_path: Path) -> None:
    result = read_and_check(prepare_text, tmp_path, "subject_id,score\nS01,\nS02,4\n")
    assert result.returncode == 0, result.stderr
