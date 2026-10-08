# Your study folder

## Set up your study folder

Copy `template/my-study` and rename it for your study:

```
my-study/
├── inputs/    input.md (your study design), your data, and an optional toy file
├── code/      the analysis script RAMM-AI writes, and sessions/ for the conversation record
├── outputs/   everything the script writes
└── envs/      the reproducible environment, if you use the reproduce skill
```

This is the [YODA layout](https://handbook.datalad.org/en/latest/basics/101-127-yoda.html):
  inputs, code, outputs and the computing environment kept apart, so anyone
  can see what produced each result.

1. Fill in `inputs/input.md`.
  It is required: it records your questions before any results exist, like a
  registered report.
  RAMM-AI can suggest text for each heading if you describe your study.
2. Keep your real data **out** of the study folder until you are ready to run
  the script.
  This is for privacy: anything the assistant opens is sent to your AI
  provider, a third party, which matters for unpublished or confidential data.
  The AI assistant only needs `input.md`.
  If you want it to see the shape of your data, add a few made-up rows as a toy
  file whose name starts with `toy_`; everything in that file is sent to the AI
  provider.
  (OpenCode users with the template config can leave their data in place: the
  config stops the assistant reading data files.
  This does not hold if you switched shell to `ask` for a free model.)
3. Open your agent in the study folder and start RAMM-AI with the command in the
  table in [install.md](install.md).

## What happens

1. RAMM-AI reads `inputs/input.md` and summarises the design back to you in
  plain language.
  It waits for your answer before writing anything.
2. It writes `code/analysis.R` and gives you the command to run.
3. You put your data file in `inputs/` and run, from the study folder:

```
Rscript code/analysis.R
```

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
- `results_group_means.csv`, `results_comparisons.csv`: estimated group means
  and the differences between groups
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

Scripts use some or all of: readr, lme4 or glmmTMB, lmerTest, emmeans,
  ggplot2, broom.mixed, dplyr, tidyr (and readxl for spreadsheets).
Scripts never install packages: if one is missing, the script stops and lists
  what to install.
