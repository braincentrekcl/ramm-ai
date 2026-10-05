# Using RAMM-AI with an institutional or local model

RAMM-AI runs through OpenCode v2 with any model that supports tool calling,
  including models hosted by your institution and models running on your own
  computer.

## Institutionally hosted models

Most institutional deployments offer an OpenAI-compatible endpoint (for example
  vLLM or LiteLLM).
Ask your IT or research computing team for the endpoint address and a model
  name, then add a provider to the `opencode.jsonc` in your study folder:

```jsonc
{
  "providers": {
    "institution": {
      "name": "My institution",
      "env": ["INSTITUTION_API_KEY"],
      "package": "@opencode/ai/providers/openai-compatible",
      "settings": { "baseURL": "https://<host>/v1" },
      "models": { "<model-id>": { "name": "<display name>" } }
    }
  },
  "model": "institution/<model-id>"
}
```

Put your key in the `INSTITUTION_API_KEY` environment variable, never in the
  file: the file sits in your study folder, which you may share.

## Local models

Start Ollama and pull a model; OpenCode finds a running Ollama server by itself
  and lists its models under `/models`.

## What the model needs

The model must support tool calling, so it can read `inputs/input.md` and write
  the script.
`docs/tested-versions.md` lists the models we have tested.
