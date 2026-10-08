# What the AI assistant can see and change

- It reads `inputs/input.md` and a `toy_` file if you name one.
  It is told never to open any other data file.
- Only OpenCode with the template config enforces that.
  On the other agents, keeping the real data out of the folder until you run the
  script is what keeps it from the assistant.
- With default settings, every agent asks before changing a file outside
  `code/`.
  Do not mark your study folder as trusted in Codex, and do not use "allow
  everything" modes for RAMM-AI (Claude Code auto or bypass, Copilot
  `--allow-all`).
- It never runs R and never installs packages.
  For a pinned environment, use the reproduce skill.
