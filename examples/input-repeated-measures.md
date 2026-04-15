# Study Design

A longitudinal study with 30 rats across 3 treatment groups (vehicle, low dose, high dose; n=10 per group). Body weight was measured weekly over 8 weeks (baseline + 7 follow-up timepoints). Each animal has one measurement per timepoint. We expect both group and time effects, and a group-by-time interaction.

# Column Mappings

- Dependent variable: `weight_g` (continuous, grams)
- Fixed effect: `treatment` (levels: vehicle, low_dose, high_dose; reference = vehicle)
- Fixed effect: `week` (levels: 0, 1, 2, 3, 4, 5, 6, 7; treat as numeric/continuous for trend, or categorical if we want per-week estimates)
- Subject ID: `rat_id` (globally unique)

# Post-Hoc Comparisons

- Compare low dose and high dose to vehicle at each timepoint
- Test the group-by-time interaction

# Data File

Path: ./data.csv

# Preferences

- Treat week as categorical (we want estimated marginal means at each timepoint)
- Package: lme4
