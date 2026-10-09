# Tested versions

Each route is tested by hand on a fresh copy of `examples/demo-autoradiography`.
A route passes when RAMM-AI stops for confirmation before writing, writes only
  `code/analysis.R` without running it, opens nothing in `inputs/` except
  `input.md`, declines to edit outputs or off-topic requests, asks for the
  session export, and the script it writes reproduces het − WT in striatum as
  −14.56 (SE 5.86).
Record the agent version, the model and the date for every test.

| Route | Agent version | Model | Date | Result | Notes |
|---|---|---|---|---|---|
| Claude Code | 2.1.277 | Opus 5 (high effort) | 2026-10-07 | Pass | Run with the tester's own setup: other plugins and personal instructions were active. Confirmed the design before writing, and said it was rewriting a broken draft before doing so. Wrote the script with shell commands inside `code/`. Did not run R. Gave only `/ramm:reproduce` and the dated export command. Matched the reference. Refusing to edit outputs and declining off-topic requests were not tested. |
| Codex | 0.160.1 | gpt-6-luna (low reasoning) | 2026-10-06 | Pass after one fix | Needed a nudge after confirmation and asked for a script name (both fixed since). Read the demo's `make_data.R`. A column-name bug in the script was fixed from the pasted error without running R. |
| GitHub Copilot CLI | 1.0.92 | Automatic selection | 2026-10-06 | Pass after one fix | Did not mention a bug it knew about. After a refused edit, tried to make the change with a shell command (rule added since). The script wrote `Rplots.pdf` outside `outputs/` (template fixed since). |
| OpenCode v2 | 2.0.24 | Qwen3.8-27B (NVFP4, medium), institutionally hosted | 2026-10-07 | Pass after three fixes | Template: denied reads of anything in `inputs/` other than `input.md` and `toy_` files; with shell denied, the model had no way round it. Skill: confirmed the design before writing, ran no R, read only `input.md` (and `outputs/analysis_log.txt` to diagnose an error), wrote only `code/analysis.R`, announced each change, and gave only `@reproduce` and `/export`. The script stopped three times (a text-wrapping error, renamed ANOVA columns, split format strings); the model fixed each from the pasted error, and on the third also fixed five similar lines that had not yet failed. Results then matched the reference. The plain-language summary garbled the per-genotype counts and described the p-value adjustment as covering all 9 comparisons rather than each region's 3. |
| OpenCode v2 | 2.0.24 | Muse Spark 1.3 Free (minimal), shell `ask` | 2026-10-07 | Pass | Ran first time; matched the reference. Refusing to edit outputs and declining off-topic requests were not tested. |

## Reproduce

Each mode is tested on a copy of `examples/demo-autoradiography` with the
  environment files written by hand from the reproduce skill's templates.
A mode passes when nothing is written beside `inputs/`, `code/`, `outputs/` and
  `envs/`, and the run reproduces het − WT in striatum as −14.56 (SE 5.86).

| Mode | Host | Docker | R | Date | Result | Notes |
|---|---|---|---|---|---|---|
| renv | macOS, Apple Silicon | — | 4.5.1 | 2026-10-09 | Pass after one fix | `Rscript code/setup_environment.R`, then `Rscript code/run_analysis.R`. Then, as a collaborator with only `envs/renv.lock`, the same setup restored all versions once it loaded the project before restoring. |
| docker | macOS, Apple Silicon | 29.4.1 | 4.4.2 (image) | 2026-10-08 | Pass after two fixes | Packages build from source on ARM: `nloptr` needs `cmake`, and the build had reported success with lme4 missing until the install step checked every package loads. |

The `docker+renv` mode was dropped on 2026-10-09: Docker alone already fixes
  every version, and the mode needed R on the host with the same version as
  the image.
