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
  example mouse, then slide, then section, then region).
Mention anything unusual, such as slide numbers that restart for every individual,
  or measurements you know are missing.

# Column Mappings (required)

- Dependent variable: `column_name` (type, units; optionally, how the values usually spread, for example a long tail of high values or many zeros)
- Fixed effect: `column_name` (categorical; levels: a, b, c; reference = a)
- Fixed effect: `column_name` (continuous, units); say categorical or
  continuous for every fixed effect, such as weeks or dose, that could be either
- Subject ID: `column_name` (globally unique)
- Nesting level: `column_name` (unique or NOT unique across subjects)

# Post-Hoc Comparisons (required)

- For example: compare each treatment with vehicle
- Or write none, if the main effect answers your question (for example a factor
  with only two levels)

# Data File (required)

- File: `data.csv` (the exact name of the data file the script will read; put
  it in this inputs folder when you are ready to run the script)

# QC Rules (optional)

- For example: exclude rows where `qc_flag` is "torn"

# Exclusions and Attrition (optional)

Individuals lost or excluded after you wrote the Study Design: who, why, and
  the date you recorded it.
Keep the Study Design numbers as planned; the script reports planned and actual
  numbers side by side.

- For example: mouse_07 died before the second session (recorded 2026-03-02)

# Preferences (optional)

- P-value adjustment: Holm, Tukey, Bonferroni, none
- Alpha: 0.05
- Centring: mean, zero or a value such as 8 weeks (for a continuous fixed
  effect that interacts with another: groups are compared at that value; mean
  is the default)

# Reproducible Environment (optional)

- Reproducible environment: container or renv

# Toy Data (optional)

- File: `toy_data.csv` (a few made-up rows with the same columns as your data;
  the name must start with toy_, and everything in it is sent to the AI
  provider)
