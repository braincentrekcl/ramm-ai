# RAMM-AI data preparation

How `code/prepare.R` turns the user's raw data files into the one long table the analysis reads.
Every study goes through it, even a study with one ready file.
Prep only finds the data in the raw files and rearranges it: it never changes a measured value.

## What prep may do

Prep may only take these steps, each followed by its check from [The checks](#the-checks):

- Read a file, or a sheet of a spreadsheet; skip the rows input.md says are not data; name the columns by position when the file has no column names.
- Read as missing only the markers input.md states (for example an empty cell, `-` or `-999`).
- Keep and rename the columns input.md names.
- Stack several files of the same kind into one table, taking an ID from the file name or sheet name where input.md says that is where it is.
- Turn a measurement spread across columns (one column per condition or time point) into one row per measurement.
- Join files on the ID they share, as input.md says.
- Change IDs only in the ways input.md states for a named file: upper or lower case, zero padding, or adding a fixed prefix or suffix.
  Never remove a prefix or suffix; add it to the other file instead.
  `readr` and `readxl` already trim spaces before and after a value; spaces inside an ID stay.

Nothing else belongs in prep:

- A value calculated from the measurements, including an average of replicates, is part of the analysis script (see [Calculated values](../SKILL.md#calculated-values)).
- Removing rows for quality reasons is a QC rule, in the analysis script.
- Any other ID fix (a typo, one ID renamed to another) is for the user to make in their own files.

## What input.md must say

The user describes their files under `Data` in input.md, in their own words.
For each file, input.md must say:

1. Its name, and the sheet for a spreadsheet; for several files of the same kind, how they are named (for example every .csv in `inputs/raw/`).
2. Whether it has column names and on which row; if it has none, what each column is by position, including an unnamed index column; any rows above or below the table that are not data.
3. What one row is.
4. Where each ID is written: in a column, or only in the file name or sheet name.
5. Any columns needed that are not already listed in `Column Mappings`, and what each one is, by name or by position.
6. Any measurement spread across columns: which columns, and what to call them together.
7. How it connects to the other files: the ID they share, and any difference in how IDs are written that an allowed ID change fixes.
8. How a missing value is written.

## Reading back the steps

From what input.md says, work out the steps, in the order the script will take them, from [What prep may do](#what-prep-may-do) only.
Put them in the design summary in plain words, one line each (for example "Stack the 24 files in inputs/raw/, taking each individual's ID from the file name"), so the user can check them before any script exists.
The script follows input.md, never the conversation: if the two disagree, say so and ask the user to update input.md.

## The script

Write `code/prepare.R`, then `code/analysis.R`, which runs it (Section 2 of `references/script.md`).
`prepare.R` starts with a header comment saying that `code/analysis.R` runs it and that it follows `Data` in inputs/input.md, then the checks from [The checks](#the-checks), unchanged.
Then one block per step: a comment saying in plain words what input.md asked for, the step, its check, and a `record_step()` line with its counts.
Read a .tsv with `readr::read_tsv()` instead of `readr::read_csv()`, with the same arguments.
Call `check_read()` straight after reading each .csv or .tsv file, giving it the same `skip`.
Read a file without column names with `col_names = FALSE`, as the pattern shows, so its first row stays data.
Read a spreadsheet column that input.md says holds dates as dates, as the pattern shows; dates in a CSV file stay as written.
Build each file pattern from how input.md says the files are named, as the pattern shows.
Read every column of every raw file as text, so prep never converts or loses a value: an ID such as `007` stays `007`, a value the user did not name as missing stays as written, and `analysis.R` turns numbers into numbers when it reads the prepared table back.
The rules for `analysis.R` in `references/script.md` apply to `prepare.R` too.

This pattern shows each kind of step; use only the ones the study needs, with the files, columns and IDs from input.md.
Every prepared table is checked for rows without an individual's ID before it is saved.
For one ready file, prep reads it, checks its columns, logs its missing values, checks every row has an ID and saves it.

```r
# --- Data preparation ---
# Run by code/analysis.R, not on its own. Follows 'Data' in inputs/input.md:
# each step only finds the data in the raw files and rearranges it; no
# measured value is changed.

# (the checks from references/prepare.md go here, unchanged)

# 1. The measurements: one .csv per individual in inputs/raw/, named by the
#    individual's ID; column names on row 3; "-" means missing.
# Names that start with a letter or digit, in any case (S01.csv or S01.CSV),
# so hidden system files such as ._S01.csv never match.
raw_files <- list.files(file.path("inputs", "raw"),
                        pattern = "^[[:alnum:]].*\\.csv$", ignore.case = TRUE,
                        full.names = TRUE)
check_files_found(raw_files, "every .csv in inputs/raw/")
per_file <- lapply(raw_files, function(f) {
  table <- readr::read_csv(f, skip = 2, na = c("", "-"),
                           col_types = readr::cols(.default = "c"))
  check_read(table, basename(f), skipped_lines = 2)
  check_columns(table, c("condition", "score"), basename(f))
  log_missing(table, basename(f))
  table$subject_id <- tools::file_path_sans_ext(basename(f))
  table[, c("subject_id", "condition", "score")]
})
rows_read <- sum(vapply(per_file, nrow, integer(1)))
measurements <- do.call(rbind, per_file)
check_rows(nrow(measurements), rows_read, "Stacking the files in inputs/raw/")
record_step(paste0("Stacked ", length(raw_files), " files from inputs/raw/, ",
                   "taking each individual's ID from the file name: ",
                   nrow(measurements), " rows"))

# 2. One row per individual: sheet 'Individuals' of inputs/individuals.xlsx,
#    IDs in column 'ID' written in lower case; column 'born' holds dates.
individuals_file <- file.path("inputs", "individuals.xlsx")
check_files_found(Filter(file.exists, individuals_file), "inputs/individuals.xlsx")
individuals <- readxl::read_excel(individuals_file, sheet = "Individuals",
                                  na = c("", "NA"), col_types = "text")
check_columns(individuals, c("ID", "group", "born"), "individuals.xlsx")
# Read as text, a date cell is Excel's day number (45231), not the date the
# user sees, so read the date columns again as dates and write them as
# 2023-11-01. A cell that is not a date stops the run (check_dates).
date_columns <- "born"
as_dates <- suppressWarnings(readxl::read_excel(
  individuals_file, sheet = "Individuals", na = c("", "NA"),
  col_types = ifelse(names(individuals) %in% date_columns, "date", "skip")))
for (column in date_columns) {
  check_dates(individuals[[column]], as_dates[[column]], column,
              "individuals.xlsx", first_row = 2)
  individuals[[column]] <- format(as.Date(as_dates[[column]]))
}
log_missing(individuals, "individuals.xlsx")
# ID change stated in inputs/input.md: make the IDs upper case.
changed_ids <- toupper(individuals$ID)
check_id_change(individuals$ID, changed_ids, "individuals.xlsx")
individuals$subject_id <- changed_ids
check_unique_ids(individuals$subject_id, "individuals.xlsx")
record_step(paste0("Read ", nrow(individuals), " individuals from ",
                   "individuals.xlsx and made their IDs upper case"))

# 3. Join the two on the individual's ID.
check_join(measurements$subject_id, individuals$subject_id, "individuals.xlsx")
rows_before <- nrow(measurements)
dat <- merge(measurements, individuals[, c("subject_id", "group")],
             by = "subject_id", all.x = TRUE, sort = FALSE)
check_rows(nrow(dat), rows_before, "Joining individuals.xlsx")
record_step(paste0("Joined individuals.xlsx on the individual's ID: ",
                   nrow(dat), " rows, every measurement matched"))

# A file without column names (input.md gives each column by position) is
# read with col_names = FALSE, so its first row stays data, then named:
# table <- readr::read_csv(f, col_names = FALSE, na = c("", "-"),
#                          col_types = readr::cols(.default = "c"))
# check_read(table, basename(f))
# check_column_count(table, 3, basename(f))
# names(table) <- c("subject_id", "condition", "score")

# A measurement spread across columns, for example 'left' and 'right', is
# turned into rows like this (two columns, so twice the rows):
# long <- tidyr::pivot_longer(wide, cols = c("left", "right"),
#                             names_to = "side", values_to = "score")
# check_rows(nrow(long), nrow(wide) * 2, "Turning the side columns into rows")

# 4. Save the prepared table, which code/analysis.R reads back.
check_ids_present(dat$subject_id, "the prepared table")
dir.create(file.path("outputs", "prepared"), showWarnings = FALSE)
readr::write_csv(dat, file.path("outputs", "prepared", "data.csv"), na = "")
record_step(paste0("Prepared table: ", nrow(dat), " rows, ", ncol(dat),
                   " columns, ", length(unique(dat$subject_id)), " individuals"))
```

The prepared table is `outputs/prepared/data.csv` unless the user asks for another name in `outputs/prepared/`.

## The checks

Every `prepare.R` starts with these functions, unchanged, and calls them after each step (see [The script](#the-script)).

<!-- chunk: prepare-checks -->
```r
# --- Checks for each preparation step ---
# The AI assistant wrote this script without opening your data files, so
# each step below is checked here. A check stops with a message saying what
# to fix; nothing is dropped or changed to make the data fit.
preparation_steps <- character(0)

# Print a step and its counts to the log, and keep it for results_summary.md.
record_step <- function(text) {
  cat(text, "\n", sep = "")
  preparation_steps <<- c(preparation_steps, text)
}

# A file described in inputs/input.md is not in inputs/.
check_files_found <- function(files, description) {
  if (length(files) == 0) {
    stop("No files found for ", description, ". Put the data files in inputs/, ",
         "or check how 'Data' in inputs/input.md names them.", call. = FALSE)
  }
}

# A column described in inputs/input.md is not in the file.
check_columns <- function(table, needed, file) {
  missing_columns <- setdiff(needed, names(table))
  if (length(missing_columns) > 0) {
    stop("These columns described in inputs/input.md are not in ", file, ": ",
         paste(missing_columns, collapse = ", "),
         ". Check their spelling, and the row the column names are on, ",
         "under 'Data' in inputs/input.md.", call. = FALSE)
  }
}

# A file without column names has more or fewer columns than described.
check_column_count <- function(table, expected, file) {
  if (ncol(table) != expected) {
    stop(file, " has ", ncol(table), " columns; inputs/input.md describes ",
         expected, ". Check the columns listed under 'Data' in inputs/input.md.",
         call. = FALSE)
  }
}

# A line of a .csv or .tsv file has more or fewer fields than the file has
# columns. readr would fill the gap with a missing value, or join the extra
# fields into the last column, so stop instead. skipped_lines is the skip
# used to read the file, so the message names the lines of the file itself.
check_read <- function(table, file, skipped_lines = 0) {
  lines <- unique(readr::problems(table)$row) + skipped_lines
  if (length(lines) > 0) {
    stop(if (length(lines) == 1) "Line " else "Lines ",
         paste(lines, collapse = ", "), " of ", file,
         if (length(lines) == 1) " does" else " do", " not have ", ncol(table),
         " fields like the rest of the file, so its values cannot be matched ",
         "to columns. Correct the file.", call. = FALSE)
  }
}

# A step lost or added rows.
check_rows <- function(rows_out, rows_expected, step) {
  if (rows_out != rows_expected) {
    stop(step, ": expected ", rows_expected, " rows, got ", rows_out,
         ". Check how the files are described under 'Data' in inputs/input.md.",
         call. = FALSE)
  }
}

# An ID change from inputs/input.md would blank an ID, or turn two
# different IDs into one.
check_id_change <- function(before, after, file) {
  blanked <- unique(before[is.na(after) & !is.na(before)])
  if (length(blanked) > 0) {
    stop("Changing the IDs in ", file, " as inputs/input.md says leaves these ",
         "IDs blank: ", paste(blanked, collapse = ", "),
         ". Check the ID change under 'Data' in inputs/input.md.", call. = FALSE)
  }
  distinct_before <- unique(before)
  groups <- split(distinct_before, after[match(distinct_before, before)])
  merged <- groups[lengths(groups) > 1]
  if (length(merged) > 0) {
    stop("Changing the IDs in ", file, " as inputs/input.md says would merge ",
         "different IDs: ",
         paste(vapply(merged, paste, character(1), collapse = " and "),
               collapse = "; "),
         ". Check which individuals these are in the file.", call. = FALSE)
  }
}

# Rows without an ID cannot be matched to an individual.
check_ids_present <- function(ids, file) {
  n_missing <- sum(is.na(ids) | ids == "")
  if (n_missing > 0) {
    stop(n_missing, if (n_missing == 1) " row in " else " rows in ", file,
         if (n_missing == 1) " has" else " have", " no ID. Fill in the IDs in the file.",
         call. = FALSE)
  }
}

# A file with one row per individual lists an individual twice.
check_unique_ids <- function(ids, file) {
  check_ids_present(ids, file)
  repeated <- unique(ids[duplicated(ids)])
  if (length(repeated) > 0) {
    stop("These IDs appear more than once in ", file, ", which inputs/input.md ",
         "says has one row per individual: ", paste(repeated, collapse = ", "),
         ".", call. = FALSE)
  }
}

# IDs as text, exactly as written; a whole number read as a number keeps
# all its digits (100000, never 1e+05).
id_text <- function(ids) {
  if (!is.numeric(ids)) return(as.character(ids))
  text <- vapply(ids, format, character(1), scientific = FALSE, trim = TRUE,
                 digits = 15)
  text[is.na(ids)] <- NA
  text
}

# Before a join: every measurement must find its individual in the other
# file. IDs are compared as text, exactly as written, so 7 matches "7" but
# not "007".
check_join <- function(ids, other_ids, other_file) {
  ids <- id_text(ids)
  other_ids <- id_text(other_ids)
  check_ids_present(ids, "the measurements")
  check_ids_present(other_ids, other_file)
  unmatched <- setdiff(ids, other_ids)
  if (length(unmatched) > 0) {
    stop("These IDs are in the measurements but not in ", other_file, ": ",
         paste(unmatched, collapse = ", "),
         ". Check how the IDs are written in each file, and any ID change ",
         "under 'Data' in inputs/input.md.", call. = FALSE)
  }
  extra <- setdiff(other_ids, ids)
  if (length(extra) > 0) {
    message("These IDs are in ", other_file, " but have no measurements: ",
            paste(extra, collapse = ", "))
  }
}

# A spreadsheet column of dates, read as dates, lost a filled-in cell that
# is not a date. first_row is the spreadsheet row of the first row of data
# (2 when the column names are on row 1), so the message names the rows the
# user sees in the spreadsheet.
check_dates <- function(as_text, as_dates, column, file, first_row) {
  lost <- which(!is.na(as_text) & as_text != "" & is.na(as_dates))
  if (length(lost) > 0) {
    stop("Column ", column, " of ", file, " should hold dates (inputs/input.md), ",
         "but ", if (length(lost) == 1) "row " else "rows ",
         paste(lost + first_row - 1, collapse = ", "), if (length(lost) == 1) " holds" else " hold",
         " something else. Correct them in the file, or leave them empty.",
         call. = FALSE)
  }
}

# How many values in each column were read as missing.
log_missing <- function(table, file) {
  counts <- colSums(is.na(table))
  counts <- counts[counts > 0]
  if (length(counts) == 0) {
    cat("No missing values in ", file, "\n", sep = "")
  } else {
    cat("Missing values in ", file, ": ",
        paste(names(counts), counts, sep = ": ", collapse = ", "), "\n", sep = "")
  }
}
```
