# Reproducible environment

The reproduce skill writes the files for a pinned environment: one with fixed
  versions of the R packages (and, in a container, of R itself), so someone
  else can run your analysis with the same versions.
It writes them into `envs/` in your study folder (the environment folder of the
  YODA layout), and any helper scripts into `code/`.

## Step by step

1. After RAMM-AI has written your analysis script, you start reproduce with
  its command in the [Quick start](index.md#quick-start).
2. Reproduce tells you which mode it will use, the R version, the snapshot
  date and the files it will write, and waits.
  You confirm, or ask for the other mode.
3. You follow `envs/README.md`, which reproduce writes, to set up the
  environment and run the analysis.

## The two modes

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
