# Reproducible environment

After the analysis script is written, start reproduce (see the table in
  [install.md](install.md)).
It writes the definition of a pinned environment into `envs/` in your study
  folder (the environment folder of the YODA layout), and any helper scripts
  into `code/`, in one of two modes:

- **`container`** (default): a container with a fixed R version, system
  libraries and packages from a dated snapshot, so everything is pinned.
  It is written as a Dockerfile, for computers with Docker, and an Apptainer
  definition, for HPC clusters with Apptainer (Singularity).
  You do not need R on your computer.
- **`renv`**: an renv lockfile, for when you have R and do not need a
  container.
  It pins the package versions; you install the recorded R version yourself
  (for example with [rig](https://github.com/r-lib/rig)).

Either way, every run also records the R and package versions in
  `outputs/provenance.csv`.

Choose the mode in `inputs/input.md`:

```markdown
# Reproducible Environment (optional)
- Reproducible environment: container
```
