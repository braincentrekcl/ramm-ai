# Your study folder

## Set up your study folder

Copy `template/my-study` and rename it for your study:

```
my-study/
├── inputs/    input.md (your study design), your data, and an optional toy file
├── code/      the analysis script RAMM-AI writes, and sessions/ for the conversation record
├── outputs/   everything the script writes
└── envs/      the reproducible environment, if you use the reproduce skill
```

This is the [YODA layout](https://handbook.datalad.org/en/latest/basics/101-127-yoda.html):
  inputs, code, outputs and the computing environment kept apart, so anyone
  can see what produced each result.

1. Fill in `inputs/input.md`.
  It is required: it records your questions before any results exist, like a
  registered report.
  RAMM-AI can suggest text for each heading if you describe your study.
2. Keep your real data **out** of the study folder until you are ready to run
  the script.
  This is for privacy: anything the assistant opens is sent to your AI
  provider, a third party, which matters for unpublished or confidential data.
  The AI assistant only needs `input.md`.
  If you want it to see the shape of your data, add a few made-up rows as a toy
  file whose name starts with `toy_`; everything in that file is sent to the AI
  provider.
  (OpenCode users with the template config can leave their data in place: the
  config stops the assistant reading data files.
  This does not hold if you switched shell to `ask` for a free model.)
3. Open your agent in the study folder and start RAMM-AI with the command in the
  table in [install.md](install.md).

Next: [Running the analysis](running-the-analysis.md).
