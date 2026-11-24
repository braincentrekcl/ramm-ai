**Before you start (delete this paragraph when you have read it):**
Keep every heading marked (required) and answer it; delete headings marked
  (optional) that you do not need, and add headings of your own for anything
  else relevant to your study.
Under each heading, replace the guidance and examples with your own answer,
  in plain English.
RAMM-AI reads everything in this file, so leftover template text can confuse
  it.
If you are not sure about a choice, leave it out or say so rather than
  guessing: RAMM-AI asks you about it.
This file records your questions before any results exist; kept under version
  control, with a dated commit before you run the analysis, it serves as a
  preregistration-style record.

# Study Design (required)

Replace this text with: how many individuals (mice, participants, donors…)
  are in each group, what was measured, and how the measurements are
  organised (for example individual, then a measurement within it, then a
  repeat of that measurement).
Mention anything unusual, such as IDs that restart for every individual, or
  measurements you know are missing.

# Column Mappings (required)

Replace these examples with one line for each column the analysis uses:

- Dependent variable: `column_name` (type, units; optionally, how the values usually spread, for example a long tail of high values or many zeros)
- Fixed effect: `column_name` (categorical; levels: a, b, c; reference = a)
- Fixed effect: `column_name` (continuous, units); for a quantity such as dose
  or weeks, say whether you want one trend (continuous) or an estimate at each
  value (categorical)
- Subject ID: `column_name` (globally unique)
- Nesting level: `column_name` (unique or NOT unique across subjects)

# Post-Hoc Comparisons (required)

Replace this text with the comparisons you want, for example "compare each
  treatment with vehicle".
Or write none, if the main effect answers your question (for example a factor
  with only two levels).

# Data (required)

Replace this text with, for each data file, in your own words:
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

Replace this text with the rows to exclude before the analysis, for example
  "exclude rows where `qc_flag` is torn".

# Exclusions and Attrition (optional)

Replace this text with the individuals lost or excluded after you wrote the
  Study Design: who, why, and the date you recorded it, for example
  "individual_07 withdrew before the second session (recorded 2026-03-02)".
Keep the Study Design numbers as planned; the script reports planned and actual
  numbers side by side.

# Preferences (optional)

Replace these examples with the choices you have made:

- P-value adjustment: Holm, Tukey, Bonferroni, none
- Alpha: 0.05
- Centring: mean, zero or a value such as 8 weeks (for each continuous fixed
  effect: group means, and with an interaction group comparisons, are given at
  that value; if you leave it out, RAMM-AI asks)

# Toy Data (optional)

Replace this text with the name of your toy file, for example `toy_data.csv`:
  a few made-up rows with the same columns as one of your data files.
The name must start with toy_, and everything in it is sent to the AI
  provider.
