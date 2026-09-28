# Study Design

SIMULATED DEMO DATA (see make_data.R); not from a real experiment.

Receptor autoradiography in wild-type (WT), heterozygous (het) and homozygous (hom) knockout mice, 10 mice per genotype (30 mice).
We measured [³H]-radioligand specific binding (µCi/g tissue equivalent) in three brain regions: striatum, sensory cortex and dorsal hippocampus.
Each mouse has two slides with 3 coronal sections each, and every slide holds sections from one mouse only:
the striatal slide, where both striatum and sensory cortex are measured on every section, and the hippocampal slide, where dorsal hippocampus is measured on every section.
On every section we drew one region of interest per region in the left hemisphere and one in the right, giving 6 measurements per region per mouse (sections 1-3, left and right).
Some sections were torn (all measurements on that section lost), some hemispheres were damaged (that side's measurements on that section lost), and one slide cracked, so mice have between 0 and 6 usable measurements per region.
We want to know whether binding differs between genotypes, and whether the genotype difference depends on brain region.

# Column Mappings

- Dependent variable: `specific_binding` (continuous, µCi/g tissue equivalent)
- Fixed effect: `genotype` (levels: WT, het, hom; reference = WT)
- Fixed effect: `region` (levels: striatum, sensory_cortex, dorsal_hippocampus)
- Subject ID: `mouse_id` (globally unique)
- Slide: `slide_id` (globally unique; two slides per mouse, 3 sections per slide)
- Section: `section` (1-3 within slide); striatum and sensory cortex are measured on the same sections
- Hemisphere: `hemisphere` (L, R; one region of interest per region per hemisphere per section)
- Replicate label: `replicate` (1L-3L, 1R-3R)

# Post-Hoc Comparisons

- Compare all three genotypes with each other (het vs WT, hom vs WT, hom vs het) within each region

# Quality Control

- Keep every mouse and every usable measurement; do not exclude mice for having few measurements.

# Data File

Path: ./data.csv

# Preferences

- Package: lme4
