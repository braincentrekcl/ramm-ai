# RAMM-AI

**Read the documentation at <https://braincentrekcl.github.io/ramm-ai/>.**

**Replicate-Aware Mixed Modelling**: an AI assistant skill that helps you
  build an R analysis project for experimental data with repeated or nested
  measurements, without needing coding experience.
It works with Claude Code, OpenAI Codex, GitHub Copilot and OpenCode.

## Examples

- **[`demo-autoradiography`](https://github.com/braincentrekcl/ramm-ai/raw/main/examples/demo-autoradiography.zip)**: simulated receptor autoradiography,
  three genotypes, three regions, slides and sections, uneven tissue loss
- **[`demo-open-field`](https://github.com/braincentrekcl/ramm-ai/raw/main/examples/demo-open-field.zip)**: simulated open-field crossover (vehicle vs
  diazepam) with missing sessions
- **[`demo-paired-markers`](https://github.com/braincentrekcl/ramm-ai/raw/main/examples/demo-paired-markers.zip)**: simulated development of two synaptic
  markers across seven ages, with a transient dip, each compared with its own
  adult level.
  Its question invites methods beyond RAMM-AI, so it shows how RAMM-AI answers
  within its models
- **`examples/input-*.md`**: further example `input.md` files

Each demo is a study folder.
Download one, unzip it where you keep your studies, then open your agent in it
  and start RAMM-AI.

## Contributing

Open pull requests against the `develop` branch, not `main`.
`main` changes only at a release, so every install gets a tested version.
[Contributing](docs/contributing.md) explains how to run the checks and the
  acceptance runs.

## Licence

MIT
