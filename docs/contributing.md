# Contributing

## Where changes go

Open pull requests against the `develop` branch, not `main`.
`main` changes only at a release, so every install gets a tested version.

## Repository checks

Run them from the repository root:

```bash
uv run --with pytest pytest tests
```

The R chunk tests need R and the R packages installed in `.github/ci/Dockerfile`.
CI runs them in that image.

## Acceptance runs

An acceptance run gives an agent a fresh copy of a demo study, has it write the analysis, runs the script and records what broke, against the criteria in [Tested versions](tested-versions.md).
They run headless in the dev image, a container with R, the R packages and every agent at the version pinned in `tests/agent-versions.json`, the versions CI checks.
Agents cannot be held at an exact version on every computer, and in the container they reach only the folders a run needs.
The harness refuses to run outside the image, stops before the first run if an agent is not at its pinned version, and stops the batch if a version changes partway through.
Pass `--model` and `--effort` to match the row in Tested versions you are comparing with, rather than relying on your account's defaults.

### Your accounts, and what a run can cost

Runs use your own subscriptions, and you need one only for the agents you test.
Check these settings before you start, so that reaching your plan's limit cannot charge you more:

- **Claude:** extra usage, in your claude.ai settings.
- **ChatGPT (Codex):** credits and automatic reload, under Settings > Usage.
  Once a plan's Codex limit is reached, Codex spends any credits you hold.
- **GitHub Copilot:** a spending budget, in your GitHub billing settings.

### Running a batch

You need Docker.
From the repository root:

```bash
python3 tests/acceptance_docker.py claude open-field --runs 3 --out <folder> --model <model> --effort <effort>
```

The first run builds the image, which takes several minutes.
Later runs reuse it.
The repository is mounted read-only, and only the `--out` folder is writable.

Each agent signs in inside the container through your own subscription:

| Agent | What it needs |
|---|---|
| Claude Code | A token from `claude setup-token`, in `CLAUDE_CODE_OAUTH_TOKEN` |
| Codex | Your Codex login on this computer (`~/.codex/auth.json`), which is mounted read-only |
| GitHub Copilot | A fine-grained personal access token owned by your personal account, with the "Copilot Requests" permission, in `COPILOT_GITHUB_TOKEN` |
| OpenCode | Nothing, for its free model |

Keep tokens however you already keep secrets, never in the repository.
The script needs the variable set when it runs, and passes it into the container by name, so the token never appears on a command line.
