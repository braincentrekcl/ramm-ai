# RAMM-AI

**Replicate-Aware Mixed Modelling**: an AI assistant skill that writes
  self-contained, glass-box R scripts for mixed-effects models in experimental
  research with repeated or nested measurements.

You describe your study design in plain English in `inputs/input.md`.
RAMM-AI writes an R script with the appropriate lme4/glmmTMB model, estimated
  marginal means, diagnostics and QC checks, with every modelling decision
  explained in comments.
You run the script yourself: the AI assistant never sees your data.

RAMM-AI works with four coding agents: Claude Code, Codex, GitHub Copilot and
  OpenCode.
Use whichever your AI provider offers; OpenCode works with almost any provider,
  including institutionally hosted and local models.

## Before you start

- R, to run the script RAMM-AI writes.
- Git, for the install commands below.
  Without git (common on managed computers), download this repository as a ZIP
  from GitHub, unzip it, and use the path of that folder wherever the commands
  below say `braincentrekcl/ramm-ai` or a GitHub URL.
  To update, download the ZIP again.

## Install

| Agent | Install | Start RAMM-AI | Start reproduce |
|---|---|---|---|
| Claude Code | `claude plugin marketplace add braincentrekcl/ramm-ai`, then `claude plugin install ramm@ramm-ai` | `/ramm:ramm` | `/ramm:reproduce` |
| Codex | `codex plugin marketplace add braincentrekcl/ramm-ai`, then `codex plugin add ramm@ramm-ai` | `$ramm:ramm` | `$ramm:reproduce` |
| GitHub Copilot (CLI and VS Code) | `copilot plugin marketplace add braincentrekcl/ramm-ai`, then `copilot plugin install ramm@ramm-ai` | `/ramm` | `/reproduce` |
| OpenCode v2 | Download this repository, then copy `opencode/opencode.jsonc` into your study folder and set the path to this repository's `skills` folder in it | `@ramm` | `@reproduce` |

OpenCode: RAMM-AI supports OpenCode v2 only (`brew install
  anomalyco/tap/opencode-v2` or `npm install -g @opencode/cli`).
OpenCode cannot currently use a GitHub Copilot Free or Student plan: it lists
  no models for them ([anomalyco/opencode#34644](https://github.com/anomalyco/opencode/issues/34644)).
With those plans, use the GitHub Copilot route instead.
OpenCode's free models do not work while the template denies shell commands
  ([anomalyco/opencode#51241](https://github.com/anomalyco/opencode/issues/51241)).
To use one, change `deny` to `ask` on the shell line, keep your data out of the
  study folder as on the other agents, and decline any command that would read
  your data.
Free models may keep or learn from what you send, so check their terms.
For institutionally hosted or local models, see
  [docs/institutional-models.md](docs/institutional-models.md).

## Set up your study folder

Copy `template/my-study` and rename it for your study:

```
my-study/
├── inputs/    input.md (your study design), your data, and an optional toy file
├── code/      the analysis script RAMM-AI writes, and sessions/ for the conversation record
└── outputs/   everything the script writes
```

1. Fill in `inputs/input.md`.
  It is required: it records your questions before any results exist, like a
  registered report.
  RAMM-AI can suggest text for each heading if you describe your study.
2. Keep your real data **out** of the study folder until you are ready to run
  the script.
  The AI assistant only needs `input.md`.
  If you want it to see the shape of your data, add a few made-up rows as a toy
  file whose name starts with `toy_`; everything in that file is sent to the AI
  provider.
  (OpenCode users with the template config can leave their data in place: the
  config stops the assistant reading data files.
  This does not hold if you switched shell to `ask` for a free model.)
3. Open your agent in the study folder and start RAMM-AI with the command in the
  table above.

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

## What the AI assistant can see and change

- It reads `inputs/input.md` and a `toy_` file if you name one.
  It is told never to open any other data file.
- Only OpenCode with the template config enforces that.
  On the other agents, keeping the real data out of the folder until you run the
  script is what keeps it from the assistant.
- With default settings, every agent asks before changing a file outside
  `code/`.
  Do not mark your study folder as trusted in Codex, and do not use "allow
  everything" modes for RAMM-AI (Claude Code auto or bypass, Copilot
  `--allow-all`).
- It never runs R and never installs packages.
  For a pinned environment, use the reproduce skill.

## Reproducible environment

After the analysis script is written, start reproduce (see the table above).
It writes the files for a pinned environment into `code/`, in one of three
  modes:

- **`docker+renv`** (default): Docker image plus an renv lockfile, maximally
  reproducible
- **`docker`**: Docker image with a pinned CRAN snapshot
- **`renv`**: R-native lockfile for users with R already installed

Choose the mode in `inputs/input.md`:

```markdown
# Reproducible Environment (optional)
- Reproducible environment: docker
```

## Examples

- **`examples/demo-autoradiography/`**: simulated receptor autoradiography,
  three genotypes, three regions, slides and sections, uneven tissue loss
- **`examples/demo-open-field/`**: simulated open-field crossover (vehicle vs
  diazepam) with missing sessions
- **`examples/input-*.md`**: further example `input.md` files

Each demo is a study folder: copy it somewhere new, open your agent in it and
  start RAMM-AI.

## R packages

Scripts use some or all of: readr, lme4 or glmmTMB, lmerTest, emmeans,
  ggplot2, broom.mixed, dplyr, tidyr (and readxl for spreadsheets).
Scripts never install packages: if one is missing, the script stops and lists
  what to install.

## Tested versions

See [docs/tested-versions.md](docs/tested-versions.md).

## Principles

- **Glass-box:** every decision is explained.
  The script teaches, not just executes.
- **Your data stays yours:** the AI assistant writes the script; you run it.
- **Reproducible:** self-contained scripts, `sessionInfo()`, and a provenance
  record of every run.
- **FAIR:** documented outputs with tidy CSV exports.

## Licence

MIT
