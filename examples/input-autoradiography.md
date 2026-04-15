# Study Design

This study has 48 subjects, split between 4 drug groups (vehicle, drug A, drug B, drug C). Each group has 12 subjects.

Measurements are of uCi/g per brain region (quantitative autoradiography). There are 12 regions of interest, and each region has 3-6 brain section replicates. There are three sections on each slide. The measurements have a slide number that is not unique (slide 1 from subject 1 is not the same slide 1 from subject 2).

Most subjects have all the regions but not all regions are on all slides or sections, and not all sections will have all regions. There might be slide-batch and subject effects.

# Column Mappings

- Dependent variable: `uci_g` (continuous, uCi/g radioligand binding density)
- Fixed effect: `drug_group` (levels: vehicle, drugA, drugB, drugC; reference = vehicle)
- Subject ID: `subject_id` (globally unique)
- Nesting - slide: `slide_num` (NOT unique across subjects)
- Nesting - section: `section_num` (NOT unique across slides)
- Region: `region` (12 ROIs; observation-level grouping)

# Post-Hoc Comparisons

- Compare each drug group (drugA, drugB, drugC) to vehicle

# Data File

Path: ./data.csv

# Preferences

- Package: lme4
- Alpha: 0.05
