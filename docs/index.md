# RAMM-AI

RAMM-AI (Replicate-Aware Mixed Modelling) is an AI assistant skill that helps
  you build an R analysis project for experimental data with repeated or nested
  measurements, without needing coding experience.
It gives you more flexibility than point-and-click statistics software, and
  every modelling decision is written down and explained in the script.

You describe your study design in plain English in `inputs/input.md`.
RAMM-AI writes a self-contained R script with the appropriate linear
  mixed-effects model, estimated marginal means, diagnostics and QC checks.
You run the script yourself, and the assistant can help you run it and
  explain its output.
RAMM-AI writes only linear mixed-effects models, or a standard linear model
  when each individual was measured once.
If your question needs another method, it says so, offers the closest
  analysis it can write, and suggests asking a statistician.
Count, proportion and binary outcomes are beyond RAMM-AI's current scope.
It flags them, and fits a linear mixed model only if you choose to continue.
Contributions that add properly validated support are welcome.

RAMM-AI works with Claude Code, OpenAI Codex, GitHub Copilot and OpenCode.
The agent and model versions we tested are listed in
  [Tested versions](tested-versions.md).
Use whichever your AI provider offers.
OpenCode works with almost any provider, including institutionally hosted and
  local models.

## Before you start

Install these first:

1. **An AI coding agent:** Claude Code, OpenAI Codex, GitHub Copilot or
   OpenCode.
   Use its desktop app or its terminal version.
   Its website will not work, because it cannot open files on your computer.
   [Installing RAMM-AI](install.md) has links to each one.
2. **[R](https://cran.r-project.org/) or
   [Docker](https://www.docker.com/products/docker-desktop/)**, to run the
   script on your computer.
   If you can use an HPC cluster with Apptainer (or Singularity), you do not
   need R or Docker.
   [Reproducible environment](reproducible-environment.md) explains how.
3. **Git is optional.**
   Git keeps every version of your files.
   If you save your study folder with it each time you run the script, you can
   always find the exact `input.md` and script that produced a set of results.

## Install

[Installing RAMM-AI](install.md) has the commands for each agent's terminal
  version and the steps for each desktop app.

## Quick start

1. Download the [study folder template](https://github.com/braincentrekcl/ramm-ai/raw/main/template/my-study.zip), unzip it where you keep
   your studies, and rename the `my-study` folder for your study.
2. Fill in `inputs/input.md`.
3. Keep your real data out of the study folder until you run the script.
  Anything the assistant opens is sent to your AI provider, a third party.
4. Open your agent in the study folder and type its start command:

   | Agent | Start RAMM-AI | Start reproduce |
   |---|---|---|
   | Claude Code | `/ramm:ramm` | `/ramm:reproduce` |
   | OpenAI Codex | `$ramm:ramm` | `$ramm:reproduce` |
   | GitHub Copilot | `/ramm` | `/reproduce` |
   | OpenCode v2 | `@ramm` | `@reproduce` |

## Examples

- **[`demo-autoradiography`](https://github.com/braincentrekcl/ramm-ai/raw/main/examples/demo-autoradiography.zip)**: simulated receptor autoradiography,
  three genotypes, three regions, slides and sections, uneven tissue loss
- **[`demo-open-field`](https://github.com/braincentrekcl/ramm-ai/raw/main/examples/demo-open-field.zip)**: simulated open-field crossover (vehicle vs
  diazepam) with missing sessions
- **[`demo-paired-markers`](https://github.com/braincentrekcl/ramm-ai/raw/main/examples/demo-paired-markers.zip)**: simulated development of two synaptic
  markers across seven ages, with a transient dip, each compared with its own
  adult level.
  Its question invites methods beyond RAMM-AI, so it shows how RAMM-AI answers
  within its models

Each demo is a study folder.
Download one, unzip it where you keep your studies, then open your agent in it
  and start RAMM-AI.

## Principles

- **Glass-box:** every decision is explained.
  The script teaches, not just executes.
- **Your data stays yours:** the AI assistant writes the script, and you run it.
- **Reproducible:** self-contained scripts, `sessionInfo()`, and a provenance
  record of every run.
- **FAIR:** a structured study design in `input.md`, reusable scripts,
  machine-readable CSV outputs and a provenance record of every run.
