# Running the analysis

## Step by step: what you do and what RAMM-AI does

1. You start RAMM-AI in your study folder, with its command in the
  [Quick start](index.md#quick-start).
  It reads `inputs/input.md` and summarises your design back to you in plain
  language.
  You check the summary and answer its questions.
  It writes nothing until you confirm.
2. RAMM-AI writes `code/prepare.R`, which turns your data files into one
  table, and `code/analysis.R`, which runs it, and gives you the command to
  run.
3. You put your data files in `inputs/` and run, from the study folder:

```
Rscript code/analysis.R
```

If you set up a [reproducible environment](reproducible-environment.md), use
  its run command from `envs/README.md` instead.

4. You read `outputs/results_summary.md` first.
  If something fails or you want a result explained, you show RAMM-AI the
  error or the outputs.
  It never changes your data or your results.
  Its changes go into the script, which you must rerun.
5. At the end, you save the conversation into `code/sessions/` with your
  agent's export command, so the record of what was asked and done stays with
  your study.
  RAMM-AI tells you how for your AI agent.

## What the script writes into `outputs/`

- `results_summary.md`: start here.
  The answer to each comparison in plain sentences, warnings, and a guide to the
  other files
- `results_group_means.csv`: estimated group means, if the model has a
  categorical factor (such as genotype)
- `results_slopes.csv`: estimated slopes, if the model has a continuous
  predictor (such as dose), as how much the outcome changes per unit
- `results_comparisons.csv`: the differences between groups, or between their
  slopes
- `results_replicate_audit_per_individual.csv`,
  `results_replicate_audit_summary.csv`: how many replicates each individual
  contributed
- `results_exclusions.csv`: measurements that were missing or removed by your QC
  rules
- `plot_hierarchy.png`, `plot_estimates.png`, `plot_residuals.png` and the other
  plots
- `prepared/data.csv`: your data files rearranged into the one table the model
  used, for you to check, with each step and its counts in the log
- the log of the run, and `provenance.csv`: a checksum of both scripts, every
  input and every output, with the version of RAMM-AI that wrote the script
  and the R and package versions, so anyone can check the results came from
  this script and these inputs

## R packages

Scripts use some or all of readr, lme4, lmerTest, emmeans,
  ggplot2, broom.mixed, dplyr, tidyr (and readxl for spreadsheets).
Scripts never install packages.
If one is missing, the script stops and lists what to install.

If you are not confident installing and updating R packages yourself, use the
  reproduce skill instead.
It writes the files for an environment with every package the script needs,
  at fixed versions.
You then set it up with one or two commands, instead of installing packages
  one by one.
See [Reproducible environment](reproducible-environment.md).
