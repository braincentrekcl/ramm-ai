<!--
RAMM-AI study design.
Fill in every heading marked (required) before you start RAMM-AI; headings
  marked (optional) can be deleted.
You can add headings of your own for anything else that describes the study.
This file records your questions before any results exist.
Kept under version control, with a dated commit before you run the analysis,
  it works like a registered report.
-->

# Study Design (required)

In plain English: how many individuals (mice, participants, donors…) are in
  each group, what was measured, and how the measurements are organised (for
  example mouse, then slide, then section, then region).
Mention anything unusual, such as slide numbers that restart for every individual,
  or measurements you know are missing.

# Column Mappings (required)

- Dependent variable: `column_name` (type, units)
- Fixed effect: `column_name` (levels: a, b, c; reference = a)
- Subject ID: `column_name` (globally unique)
- Nesting level: `column_name` (unique or NOT unique across subjects)

# Post-Hoc Comparisons (required)

- For example: compare each treatment with vehicle

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

- Package: lme4 or glmmTMB
- Family: gaussian, Gamma, poisson, etc.
- P-value adjustment: Holm, Tukey, Bonferroni, none
- Alpha: 0.05

# Reproducible Environment (optional)

- Reproducible environment: container or renv

# Toy Data (optional)

- File: `toy_data.csv` (a few made-up rows with the same columns as your data;
  the name must start with toy_, and everything in it is sent to the AI
  provider)
