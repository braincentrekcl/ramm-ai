# RAMM-AI

**Reproducible Automated Mixed Models** — a Claude Code plugin that generates self-contained, glass-box R scripts for mixed-effects models in preclinical research.

You describe your study design in plain English. RAMM generates a fully runnable R script with the appropriate lme4/glmmTMB model, estimated marginal means, diagnostics, and QC checks — with every modelling decision explained in inline comments.

## Installation

In Claude Code:

```
/install-plugin braincentrekcl/ramm-ai
```

Or from a local directory during development:

```
/install-plugin /path/to/ramm-ai
```

## Usage

This plugin provides two skills:

- **`/ramm:ramm`** — generate a mixed-effects analysis R script from a plain-English study design
- **`/ramm:reproduce`** — generate a reproducible environment (Docker and/or renv) for an existing analysis script

### Generating the analysis script

1. Create an `input.md` file describing your study design (see format below)
2. Place your data file (CSV) in the same directory
3. Run:

```
/ramm:ramm input.md
```

Or simply `/ramm:ramm` if your file is named `input.md`.

RAMM will parse your study design, validate it against your data (if available), and generate a self-contained R script.

### Generating a reproducible environment

After your analysis script has been generated, run:

```
/ramm:reproduce analysis.R
```

This produces a pinned environment so collaborators can reproduce your results exactly. Three modes are supported:

- **`docker+renv`** (default) — Docker image + renv lockfile, maximally reproducible
- **`docker`** — Docker image with pinned CRAN snapshot
- **`renv`** — R-native lockfile for users with R already installed

You can choose the mode by adding to your `input.md`:

```markdown
# Reproducible environment
- Reproducible environment: docker
```

## Input File Format

Your `input.md` should contain these sections:

### Study Design (required)

Plain English description of your experiment: total N, group sizes, what was measured, the hierarchy of your data (what is nested within what), and any known issues.

### Column Mappings (required)

Map your data columns to their roles:

```markdown
- Dependent variable: `column_name` (type, units)
- Fixed effect: `column_name` (levels: a, b, c; reference = a)
- Subject ID: `column_name` (globally unique)
- Nesting level: `column_name` (unique or NOT unique across subjects)
```

### Post-Hoc Comparisons (required)

What comparisons you want, in plain English:

```markdown
- Compare each treatment to vehicle
- Pairwise comparisons within genotype
```

### Data File (optional)

```markdown
Path: ./data.csv
```

### Preferences (optional)

Override defaults if needed:

```markdown
- Package: glmmTMB
- Family: Gamma
- P-value adjustment: Tukey
```

### Reproducible environment (optional)

Request a pinned environment alongside the analysis script:

```markdown
- Reproducible environment: docker+renv
- R version: 4.4.2
- Snapshot date: 2025-01-15
```

## What You Get

An R script (`analysis.R`) containing:

| Section | Contents |
|---------|----------|
| Header | Study description, what was specified |
| Environment | Package loading, reproducibility setup |
| Data prep | Loading, factor encoding, unique ID creation |
| Exploration | Summary stats, N per cell, missing data |
| Hierarchy diagram | ASCII tree of the nesting structure |
| Model | Formula with commented rationale for every term |
| Diagnostics | Convergence, singular fit, residual plots, QQ |
| Summary | Coefficients, ANOVA, confidence intervals |
| Post-hoc | emmeans with specified contrasts |
| Plots | Publication-ready (300 dpi PNG) |
| Export | Tidy results as CSV via broom.mixed |
| Session info | Full R environment for reproducibility |

## Examples

See the `examples/` directory for complete input files:

- **input-autoradiography.md** — brain region autoradiography with nested slides/sections
- **input-simple-two-group.md** — minimal two-group comparison
- **input-repeated-measures.md** — longitudinal repeated measures with group x time interaction

## R Packages Required

The generated scripts will use some or all of these (installed automatically if missing):

- lme4 / glmmTMB
- lmerTest
- emmeans
- ggplot2
- broom.mixed
- dplyr, tidyr

## Principles

- **Glass-box:** Every decision is explained. The script teaches, not just executes.
- **Reproducible:** Self-contained scripts with `set.seed()`, `sessionInfo()`, and version tracking.
- **FAIR:** Well-documented outputs with tidy CSV exports.
- **Transparent:** You can read exactly what model was fit and why.

## License

MIT
