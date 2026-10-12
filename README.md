# RAMM-AI

**Replicate-Aware Mixed Modelling**: an AI assistant skill that writes
  self-contained, glass-box R scripts for mixed-effects models in experimental
  research with repeated or nested measurements.

You describe your study design in plain English in `inputs/input.md`.
RAMM-AI writes an R script with the appropriate linear mixed-effects model, estimated
  marginal means, diagnostics and QC checks, with every modelling decision
  explained in comments.
You run the script yourself, and the assistant can help you run it and
  explain its output.

RAMM-AI works with four coding agents: Claude Code, Codex, GitHub Copilot and
  OpenCode.
Use whichever your AI provider offers; OpenCode works with almost any provider,
  including institutionally hosted and local models.

## Before you start

- An AI coding agent: Claude Code, Codex, GitHub Copilot or OpenCode.
- R to run the script, or a container instead of installing R: Docker, or
  Apptainer on an HPC cluster (see
  [Reproducible environment](docs/reproducible-environment.md)).
- Git is optional.
  Without it, download this repository as a ZIP from GitHub, unzip it, and use
  the path of that folder wherever the commands below say
  `braincentrekcl/ramm-ai` or a GitHub URL.
  To update, download the ZIP again.
  Version control is good practice for your study when you are ready for it,
  but you do not need to learn git to use RAMM-AI.

## Install

| Agent | Install | Start RAMM-AI | Start reproduce |
|---|---|---|---|
| Claude Code | `claude plugin marketplace add braincentrekcl/ramm-ai`, then `claude plugin install ramm@ramm-ai` | `/ramm:ramm` | `/ramm:reproduce` |
| Codex | `codex plugin marketplace add braincentrekcl/ramm-ai`, then `codex plugin add ramm@ramm-ai` | `$ramm:ramm` | `$ramm:reproduce` |
| GitHub Copilot (CLI and VS Code) | `copilot plugin marketplace add braincentrekcl/ramm-ai`, then `copilot plugin install ramm@ramm-ai` | `/ramm` | `/reproduce` |
| OpenCode v2 | Download this repository, then copy `opencode/opencode.jsonc` into your study folder and set the path to this repository's `skills` folder in it | `@ramm` | `@reproduce` |

For app installs and OpenCode notes, see [docs/install.md](docs/install.md).

## Quick start

1. Copy `template/my-study` and rename it for your study.
2. Fill in `inputs/input.md`.
3. Keep your real data out of the study folder until you run the script.
  This is for privacy: anything the assistant opens is sent to your AI
  provider, a third party.
4. Open your agent in the study folder and start RAMM-AI with the command above.

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
