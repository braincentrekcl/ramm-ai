# Reproducible environment

After the analysis script is written, start reproduce (see the table in
  [install.md](install.md)).
It writes the files for a pinned environment into `envs/` in your study folder
  (the environment folder of the YODA layout), in one of three modes:

- **`docker+renv`** (default if you have R and Docker): Docker image plus an
  renv lockfile, maximally reproducible.
  Whoever creates the environment needs R once, to write the lockfile;
  collaborators who receive the lockfile need only Docker.
- **`docker`** (default if you have Docker but not R): Docker image with a
  pinned CRAN snapshot.
  You do not need R on your computer at all.
- **`renv`** (default if you have R but not Docker): R-native lockfile.

If `inputs/input.md` does not name a mode, reproduce asks whether you have R
  and Docker installed and picks for you.

Choose the mode in `inputs/input.md`:

```markdown
# Reproducible Environment (optional)
- Reproducible environment: docker
```
