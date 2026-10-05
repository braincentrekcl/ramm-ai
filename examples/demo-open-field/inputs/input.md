# Study Design

SIMULATED DEMO DATA (see code/make_data.R); not from a real experiment.

Open-field test after acute diazepam, crossover design.
12 mice were each tested twice, once after vehicle and once after diazepam, with a one-week washout between sessions.
Order was counterbalanced: 6 mice received vehicle first and 6 received diazepam first.
Video tracking scored time spent in the centre zone during each 10-minute session.
Three videos were corrupted and could not be scored, so three mice have a result for only one of the two conditions.

# Column Mappings

- Dependent variable: `centre_time_s` (continuous, seconds in the centre zone per 10-minute session)
- Fixed effect: `treatment` (levels: vehicle, diazepam; reference = vehicle); within-subject
- Fixed effect: `session` (1, 2); first or second test, to account for familiarity with the arena
- Subject ID: `mouse_id` (globally unique)
- Order: `order` (vehicle_first, diazepam_first); fully determined by treatment and session

# Post-Hoc Comparisons

- Compare diazepam with vehicle

# Quality Control

- Keep every mouse, including those with only one condition; do not exclude mice for a missing session.

# Data File

- File: `data.csv`

# Preferences

- Package: lme4
