# Reproducible environment

After the analysis script is written, start reproduce (see the table in
  [install.md](install.md)).
It writes the definition of a pinned environment into `envs/` in your study
  folder (the environment folder of the YODA layout), and any helper scripts
  into `code/`, in one of two modes:

- **`docker`** (default): a Docker image with a fixed R version and packages
  from a dated snapshot, so every package version is fixed.
  You do not need R on your computer at all, only Docker.
- **`renv`**: an renv lockfile, for when you cannot use Docker but have R.
  Whoever receives the study installs exactly the recorded versions.

Either way, every run also records the R and package versions in
  `outputs/provenance.csv`.

Choose the mode in `inputs/input.md`:

```markdown
# Reproducible Environment (optional)
- Reproducible environment: docker
```
