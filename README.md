# RAMM-AI

**Replicate-Aware Mixed Modelling**: an AI assistant skill that helps you
  build an R analysis project for experimental data with repeated or nested
  measurements, without needing coding experience.
It gives you more flexibility than point-and-click statistics software, and
  every modelling decision is written down and explained in the script.

You describe your study design in plain English in `inputs/input.md`.
RAMM-AI writes a self-contained R script with the appropriate linear
  mixed-effects model, estimated marginal means, diagnostics and QC checks.
You run the script yourself, and the assistant can help you run it and
  explain its output.
RAMM-AI writes only linear mixed-effects models (or a standard linear model
  when each individual was measured once): if your question needs another
  method, it says so, offers the closest analysis it can write, and suggests
  asking a statistician.
Count, proportion and binary outcomes are beyond RAMM-AI's current scope: it
  flags them and fits a linear mixed model only if you choose to continue.
Contributions that add properly validated support are welcome.

RAMM-AI works with four coding agents: Claude Code, Codex, GitHub Copilot and
  OpenCode.
The agent and model versions we tested are listed in
  [Tested versions](docs/tested-versions.md).
Use whichever your AI provider offers; OpenCode works with almost any provider,
  including institutionally hosted and local models.

## Before you start

Install these first:

1. **An AI coding agent:** Claude Code, Codex, GitHub Copilot or OpenCode.
   Use its desktop app or its terminal version.
   Its website will not work, because it cannot open files on your computer.
   [Installing RAMM-AI](docs/install.md) has links to each one.
2. **[R](https://cran.r-project.org/) or
   [Docker](https://www.docker.com/products/docker-desktop/)**, to run the
   script on your computer.
   If you can use an HPC cluster with Apptainer (or Singularity), you do not
   need R or Docker: see
   [Reproducible environment](docs/reproducible-environment.md).
3. **Git is optional.**
   Without it, download this repository as a ZIP from GitHub, unzip it, and use
   the path of that folder wherever the install steps say
   `braincentrekcl/ramm-ai` or a GitHub URL.
   To update, download the ZIP again.
   Version control is good practice for your study when you are ready for it,
   but you do not need to learn git to use RAMM-AI.

## Install

Follow [Installing RAMM-AI](docs/install.md): it has the commands for each
  agent's terminal version, and the steps for each desktop app.

## Quick start

1. Copy `template/my-study` and rename it for your study.
2. Fill in `inputs/input.md`.
3. Keep your real data out of the study folder until you run the script.
  This is for privacy: anything the assistant opens is sent to your AI
  provider, a third party.
4. Open your agent in the study folder and type its start command:

   | Agent | Start RAMM-AI | Start reproduce |
   |---|---|---|
   | Claude Code | `/ramm:ramm` | `/ramm:reproduce` |
   | Codex | `$ramm:ramm` | `$ramm:reproduce` |
   | GitHub Copilot | `/ramm` | `/reproduce` |
   | OpenCode v2 | `@ramm` | `@reproduce` |

## Documentation

- [Installing RAMM-AI](docs/install.md)
- [Setting up your study folder](docs/study-folder.md)
- [Running the analysis and what the script writes](docs/running-the-analysis.md)
- [What the AI assistant can see and change](docs/privacy-and-safety.md)
- [Reproducible environment](docs/reproducible-environment.md)
- [Institutional and local models](docs/institutional-and-local-models.md)
- [Tested versions](docs/tested-versions.md)

## Examples

- **`examples/demo-autoradiography/`**: simulated receptor autoradiography,
  three genotypes, three regions, slides and sections, uneven tissue loss
- **`examples/demo-open-field/`**: simulated open-field crossover (vehicle vs
  diazepam) with missing sessions
- **`examples/demo-paired-markers/`**: simulated development of two synaptic
  markers across seven ages, with a transient dip, each compared with its own
  adult level; the question invites methods beyond RAMM-AI, so it shows how
  RAMM-AI answers within its models
- **`examples/input-*.md`**: further example `input.md` files

Each demo is a study folder: copy it somewhere new, open your agent in it and
  start RAMM-AI.

## Principles

- **Glass-box:** every decision is explained.
  The script teaches, not just executes.
- **Your data stays yours:** the AI assistant writes the script; you run it.
- **Reproducible:** self-contained scripts, `sessionInfo()`, and a provenance
  record of every run.
- **FAIR:** a structured study design in `input.md`, reusable scripts,
  machine-readable CSV outputs and a provenance record of every run.

## Licence

MIT
