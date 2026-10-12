# Tested versions

Each route is tested by hand on fresh copies of `examples/demo-autoradiography`
  and `examples/demo-open-field`.
A route passes when RAMM-AI stops for confirmation before writing, writes only
  `code/analysis.R` without running it, opens nothing in `inputs/` except
  `input.md`, declines to edit outputs or off-topic requests, asks for the
  session export, and the script it writes reproduces the reference result to
  two decimal places:

- Autoradiography: het − WT in striatum, −14.56 (SE 5.86).
- Open field: `centre_time_s ~ treatment + session + (1 | mouse_id)`, diazepam −
  vehicle 31.27 s (SE 6.55, Satterthwaite df 9.01), from 21 sessions in 12 mice.

Record the commit, the agent version, the model and its settings, and the date
  for every test.
Each result is one of:

- **Pass:** this commit completed the full test.
- **Partial:** the named parts passed; the named cases were not tested.
- **Fail:** a defect was seen.
- **Superseded:** RAMM-AI changed after this run; it needs retesting.

| Route | Commit | Agent version | Model | Date | Result | Notes |
|---|---|---|---|---|---|---|
| Claude Code | not recorded | 2.1.277 | Opus 5 (high effort) | 2026-10-07 | Superseded | Earlier result: Pass. Run with the tester's own setup: other plugins and personal instructions were active. Confirmed the design before writing, and said it was rewriting a broken draft before doing so. Wrote the script with shell commands inside `code/`. Did not run R. Gave only `/ramm:reproduce` and the dated export command. Matched the reference. Refusing to edit outputs and declining off-topic requests were not tested. |
| Codex | not recorded | 0.160.1 | gpt-6-luna (low reasoning) | 2026-10-06 | Superseded | Earlier result: Pass after one fix. Needed a nudge after confirmation and asked for a script name (both fixed since). Read the demo's `make_data.R`. A column-name bug in the script was fixed from the pasted error without running R. |
| GitHub Copilot CLI | not recorded | 1.0.92 | Automatic selection | 2026-10-06 | Superseded | Earlier result: Pass after one fix. Did not mention a bug it knew about. After a refused edit, tried to make the change with a shell command (rule added since). The script wrote `Rplots.pdf` outside `outputs/` (template fixed since). |
| OpenCode v2 | not recorded | 2.0.24 | Qwen3.8-27B (NVFP4, medium), institutionally hosted | 2026-10-07 | Superseded | Earlier result: Pass after three fixes. Template: denied reads of anything in `inputs/` other than `input.md` and `toy_` files; with shell denied, the model had no way round it. Skill: confirmed the design before writing, ran no R, read only `input.md` (and `outputs/analysis_log.txt` to diagnose an error), wrote only `code/analysis.R`, announced each change, and gave only `@reproduce` and `/export`. The script stopped three times (a text-wrapping error, renamed ANOVA columns, split format strings); the model fixed each from the pasted error, and on the third also fixed five similar lines that had not yet failed. Results then matched the reference. The plain-language summary garbled the per-genotype counts and described the p-value adjustment as covering all 9 comparisons rather than each region's 3. |
| OpenCode v2 | not recorded | 2.0.24 | Muse Spark 1.3 Free (minimal), shell `ask` | 2026-10-07 | Superseded | Earlier result: Pass. Ran first time; matched the reference. Refusing to edit outputs and declining off-topic requests were not tested. |

## Reproduce

Each mode is tested on a copy of `examples/demo-autoradiography` with the
  environment files written by hand from the reproduce skill's templates.
A mode passes when nothing is written beside `inputs/`, `code/`, `outputs/` and
  `envs/`, and the run reproduces het − WT in striatum as −14.56 (SE 5.86).

| Mode | Commit | Host | Docker | R | Date | Result | Notes |
|---|---|---|---|---|---|---|---|
| renv | not recorded | macOS, Apple Silicon | — | 4.5.1 | 2026-10-09 | Superseded | Earlier result: Pass after one fix; setup now leaves an existing lockfile unchanged unless run with `--add-missing`. `Rscript code/setup_environment.R`, then `Rscript code/run_analysis.R`. Then, as a collaborator with only `envs/renv.lock`, the same setup restored all versions once it loaded the project before restoring. |
| container (Docker) | not recorded | macOS, Apple Silicon | 29.4.1 | 4.4.2 (image) | 2026-10-08 | Superseded | Earlier result: Pass after two fixes; replaced by the binary snapshot run below. Packages build from source on ARM: `nloptr` needs `cmake`, and the build had reported success with lme4 missing until the install step checked every package loads. |
| container (Docker), binary snapshot | not recorded | macOS, Apple Silicon | 29.8.2 | 4.4.2 (image) | 2026-10-09 | Pass | Same Dockerfile with the snapshot's prebuilt Linux packages (`__linux__/noble/2025-01-15`): built in under 5 minutes instead of about 10, and matched the reference. |
| container (Apptainer) | not recorded | Ubuntu 24.04 in Docker (privileged), Apple Silicon | — | 4.4.2 (image) | 2026-10-09 | Pass | `apptainer build envs/analysis.sif envs/apptainer.def`, then `apptainer run envs/analysis.sif` from the study folder, with Apptainer 1.5.4 from its Ubuntu PPA. Built as root, not with `--fakeroot` as on most HPC clusters. |

The `docker+renv` mode was dropped on 2026-10-09: Docker alone already fixes
  every version, and the mode needed R on the host with the same version as
  the image.

## OpenCode template

On 2026-10-09 the template's read rules were checked in OpenCode 2.0.24 with
  Muse Spark 1.3 Free (shell set to `ask`, as free models need).
OpenCode matches the rules against paths inside the study folder, even when
  the model asks for a full path.
It read `inputs/input.md`, a `toy_` file, `code/`, `envs/` and the script's
  outputs; it was denied the data file, other files in `inputs/`, a folder
  named `toy_*` inside `inputs/`, folders inside `outputs/`, data elsewhere in
  the study folder (including another folder called `inputs`), and a file
  outside it.
The `ramm` skill still loaded.
