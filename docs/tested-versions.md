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
| Claude Code | | | | | |
| Codex | | | | | |
| GitHub Copilot CLI | | | | | |
| Gemini CLI | | | | | |
| OpenCode v2 | | | | | |
