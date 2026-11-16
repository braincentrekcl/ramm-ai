# Study Design

A simple two-group comparison. 20 mice were randomly assigned to either a treatment group (n=10) or a vehicle control group (n=10). Body weight (grams) was measured once per animal. There is no nesting beyond the subject level.

# Column Mappings

- Dependent variable: `body_weight` (continuous, grams)
- Fixed effect: `treatment` (levels: vehicle, treated; reference = vehicle)
- Subject ID: `animal_id` (globally unique)

# Post-Hoc Comparisons

- Compare treated to vehicle

# Data

- `data.csv`: column names on row 1, nothing else above or below the table;
  one row is one measurement; the individual's ID is in `animal_id`; missing
  values are empty cells.
