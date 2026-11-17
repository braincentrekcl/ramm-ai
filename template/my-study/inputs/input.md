<!--
RAMM-AI study design.
Fill in every heading marked (required) before you start RAMM-AI; headings
  marked (optional) can be deleted.
You can add headings of your own for anything else that describes the study.
This file records your questions before any results exist.
Kept under version control, with a dated commit before you run the analysis,
  it serves as a preregistration-style record.
-->

# Study Design (required)

In plain English: how many individuals (mice, participants, donors…) are in
  each group, what was measured, and how the measurements are organised (for
  example individual, then a measurement within it, then a repeat of that
  measurement).
Mention anything unusual, such as IDs that restart for every individual, or
  measurements you know are missing.

# Column Mappings (required)

- Dependent variable: `column_name` (type, units; optionally, how the values usually spread, for example a long tail of high values or many zeros)
- Fixed effect: `column_name` (categorical; levels: a, b, c; reference = a)
- Fixed effect: `column_name` (continuous, units); for a quantity such as dose
  or weeks, say whether you want one trend (continuous) or an estimate at each
  value (categorical)
- Subject ID: `column_name` (globally unique)
- Nesting level: `column_name` (unique or NOT unique across subjects)

# Post-Hoc Comparisons (required)

- For example: compare each treatment with vehicle
- Or write none, if the main effect answers your question (for example a factor
  with only two levels)

# Data (required)

For each data file, say in your own words:
- its name (and the sheet, for a spreadsheet); if the data is split into
  several files of the same kind (for example one per individual), how the
  files are named
- whether it has column names, and on which row; anything above or below the
  table that is not data (settings, a summary row)
- what one row is (one individual, or one of several measurements of an
  individual?)
- where each ID is written (the individual's, and each sub-measurement's, if
  it has one)
- which columns you need and what each one is
- if one kind of measurement is spread over several columns (for example one
  column per condition or time point), which columns, and what to call them
  together
- how a missing value is written (empty, NA, -, -999…)
- if you have more than one file, how they connect (for example "the ID
  column in the second file is the individual's ID"), and any difference in
  how IDs are written (upper or lower case, zero padding, a prefix)

Put the files in this inputs folder when you are ready to run the script.

# QC Rules (optional)

- For example: exclude rows where `qc_flag` is "torn"

# Exclusions and Attrition (optional)

Individuals lost or excluded after you wrote the Study Design: who, why, and
  the date you recorded it.
Keep the Study Design numbers as planned; the script reports planned and actual
  numbers side by side.

- For example: individual_07 withdrew before the second session (recorded 2026-03-02)

# Preferences (optional)

- P-value adjustment: Holm, Tukey, Bonferroni, none
- Alpha: 0.05
- Centring: mean, zero or a value such as 8 weeks (for each continuous fixed
  effect: group means, and with an interaction group comparisons, are given at
  that value; if you leave it out, RAMM-AI asks)

# Reproducible Environment (optional)

- Reproducible environment: container or renv

# Toy Data (optional)

- File: `toy_data.csv` (a few made-up rows with the same columns as one of
  your data files; the name must start with toy_, and everything in it is
  sent to the AI provider)
