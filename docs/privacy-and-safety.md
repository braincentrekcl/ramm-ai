# What the AI assistant can see and change

Anything the assistant opens is sent to your AI provider.

- It reads `inputs/input.md`, and a `toy_` file in `inputs/` if `input.md`
  names one.
  It is told never to open any other file in `inputs/`.
- It reads the files it writes in `code/`.
- When you ask it to explain results or an error, it reads what the script
  wrote in `outputs/`: the log, the results tables, the summary and the plots.
  These hold no measurements from your data, but `results_exclusions.csv` and
  the replicate audit list your individuals' IDs.
  If those IDs could identify someone (for example participant codes linked to
  names), use coded IDs in your data.
- Only OpenCode with the template config enforces these limits.
  On the other agents, keeping the real data out of the folder until you run the
  script is what keeps it from the assistant.
- With default settings, every agent asks before changing a file; the OpenCode
  template lets it change files in `code/` and `envs/` only.
  Do not mark your study folder as trusted in Codex, and do not use "allow
  everything" modes for RAMM-AI (Claude Code auto or bypass, Copilot
  `--allow-all`).
  In those modes the agent can change or delete files anywhere in the study
  folder, including your data and results, and run commands that read your
  data, without asking you first.
  RAMM-AI tells it not to, but nothing stops it if it gets that wrong.
- It never runs R and never installs packages.
  For a pinned environment, use the reproduce skill.
