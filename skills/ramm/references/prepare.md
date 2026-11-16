# RAMM-AI data preparation

How `code/prepare.R` turns the user's raw data files into the one long table the analysis reads.
Every study goes through it, even a study with one ready file.
Prep only finds the data in the raw files and rearranges it: it never changes a measured value.

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
