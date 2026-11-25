# Your study folder

## Set up your study folder

Download the [study folder template](https://github.com/braincentrekcl/ramm-ai/raw/main/template/my-study.zip), unzip it where you keep your
  studies, and rename the `my-study` folder for your study:

```
my-study/
├── inputs/    input.md (your study design), your raw data files, and an optional toy file
├── code/      prepare.R and analysis.R, the scripts RAMM-AI writes, and sessions/ for the conversation record
├── outputs/   everything the scripts write, with your data rearranged into one table in prepared/
└── envs/      the reproducible environment, if you use the reproduce skill
```

This is the [YODA layout](https://handbook.datalad.org/en/latest/basics/101-127-yoda.html),
  which keeps inputs, code, outputs and the computing environment apart, so
  anyone can see what produced each result.
Your data files go in `inputs/` as your software exported them.
`prepare.R` turns them into the one table the model needs, and never changes a measured
  value.
If RAMM-AI should analyse another tool's output (for example quality metrics
  from MRIQC), that output is an input.
Put it in `inputs/`, as a copy or as a DataLad subdataset.
Folders other tools write in `outputs/` are left alone.
RAMM-AI never reads them, and its provenance record never lists them.

1. Fill in `inputs/input.md`.
  It is required, because it records your questions before any results exist.
  Kept under version control, with a dated commit before you run the analysis,
  it serves as a preregistration-style record.
  RAMM-AI can suggest text for each heading if you describe your study.
2. Keep your real data **out** of the study folder until you are ready to run
  the script.
  Anything the assistant opens is sent to your AI provider, a third party,
  which matters for unpublished or confidential data.
  The AI assistant only needs `input.md`.
  If you want it to see the shape of your data, add a few made-up rows as a toy
  file whose name starts with `toy_`.
  Everything in that file is sent to the AI provider.
  (OpenCode users with the template config can leave their data in place,
  because the config lets the assistant read only `input.md` and `toy_` files in `inputs/`.
  This does not hold if you switched shell to `ask` for a free model.)
3. Open your agent in the study folder and start RAMM-AI with the command in the
  [Quick start](index.md#quick-start).

Next: [Running the analysis](running-the-analysis.md).
