# Reproducible environment

After the analysis script is written, start reproduce (see the table in
  [install.md](install.md)).
It writes the files for a pinned environment into `code/`, in one of three
  modes:

- **`docker+renv`** (default): Docker image plus an renv lockfile, maximally
  reproducible
- **`docker`**: Docker image with a pinned CRAN snapshot
- **`renv`**: R-native lockfile for users with R already installed

Choose the mode in `inputs/input.md`:

```markdown
# Reproducible Environment (optional)
- Reproducible environment: docker
```
