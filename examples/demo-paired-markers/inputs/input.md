# Study Design

SIMULATED DEMO DATA (see code/make_data.R); not from a real experiment.

## Overview

This study characterises the postnatal developmental trajectories of two synaptic markers in mouse somatosensory cortex.
28 mice were studied: 4 at each of 7 ages (P7, P10, P14, P21, P28, P42 and adult).
Each mouse contributed 3 sections, and both markers were imaged on every section, so the two markers are paired within each section.
Section numbers (1-3) restart in every mouse.

## Scientific question

The central question is whether the two markers mature along the same trajectory relative to their own adult levels.
Because the markers differ substantially in absolute intensity, a direct comparison of raw values would be misleading; what matters is each marker's profile expressed relative to its adult reference, and whether the two markers diverge from that reference proportionally or one matures later than the other.

## Key observation

Pilot imaging suggests the trajectories are clearly non-linear: rather than rising steadily, both markers show a transient dip, falling from P14 to P21 before recovering to roughly their P14 level by P28.
This non-monotonic pattern is a key feature of the data and the analysis should account for it appropriately.

Age is treated as a categorical factor (seven discrete age groups), not as a continuous variable.

# Column Mappings

- Dependent variable: `fluorescence` (continuous, mean fluorescence in arbitrary units; always positive, with a long tail of high values)
- Fixed effect: `age_group` (categorical; levels: P7, P10, P14, P21, P28, P42, adult; reference = adult); between-subject
- Fixed effect: `marker` (categorical; levels: marker_a, marker_b; reference = marker_a); within-subject, both markers on every section
- Subject ID: `mouse_id` (globally unique)
- Nesting level: `section` (1-3, NOT unique across mice)

# Post-Hoc Comparisons

- For each marker, compare every age with adult.
- Test whether the two markers differ in how far each age is from adult, relative to each marker's own adult level (proportional divergence).

# Data File

- File: `data.csv`
