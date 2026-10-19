# Running the analysis

## What happens

1. RAMM-AI reads `inputs/input.md` and summarises the design back to you in
  plain language.
  It waits for your answer before writing anything.
2. It writes `code/analysis.R` and gives you the command to run.
3. You put your data file in `inputs/` and run, from the study folder:

```
Rscript code/analysis.R
```

If you set up a [reproducible environment](reproducible-environment.md), use
  its run command from `envs/README.md` instead.

4. Start with `outputs/results_summary.md`.
  If something fails or you want a result explained, show RAMM-AI the error or
  the outputs.
  It never changes your data or your results: every change goes through the
  script, and you rerun it.
5. At the end, RAMM-AI asks you to save the conversation into `code/sessions/`
  with your agent's export command, so the record of what was asked and done
  stays with your study.

The script writes into `outputs/`:

- `results_summary.md`: start here.
  The answer to each comparison in plain sentences, warnings, and a guide to the
  other files
- `results_group_means.csv`: estimated group means, if the model has a
  categorical factor (such as genotype)
- `results_slopes.csv`: estimated slopes, if the model has a continuous
  predictor (such as dose): how much the outcome changes per unit
- `results_comparisons.csv`: the differences between groups, or between their
  slopes
- `results_replicate_audit_per_individual.csv`,
  `results_replicate_audit_summary.csv`: how many replicates each individual
  contributed
- `results_exclusions.csv`: measurements that were missing or removed by your QC
  rules
- `plot_hierarchy.png`, `plot_emmeans.png`, `plot_residuals.png` and the other
  plots
- the log of the run, and `provenance.csv`: a checksum of the script, every
  input and every output, with the R and package versions, so anyone can check
  the results came from this script and these inputs

## R packages

Scripts use some or all of: readr, lme4, lmerTest, emmeans,
  ggplot2, broom.mixed, dplyr, tidyr (and readxl for spreadsheets).
Scripts never install packages: if one is missing, the script stops and lists
  what to install.
