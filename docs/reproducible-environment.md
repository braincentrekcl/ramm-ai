# Reproducible environment

After the analysis script is written, start reproduce (see the table in
  [install.md](install.md)).
It writes the files for a pinned environment into `envs/` in your study folder
  (the environment folder of the YODA layout), in one of three modes:

- **`docker+renv`** (default if you have R): Docker image plus an renv
  lockfile, maximally reproducible.
  It needs R once, to write the lockfile; after that the analysis runs in
  Docker.
- **`docker`** (default if you do not have R): Docker image with a pinned CRAN
  snapshot.
  You do not need R on your computer at all, only Docker.
- **`renv`**: R-native lockfile for users with R already installed.

If `inputs/input.md` does not name a mode, reproduce asks whether you have R
  installed and picks for you.

Choose the mode in `inputs/input.md`:

```markdown
# Reproducible Environment (optional)
- Reproducible environment: docker
```
