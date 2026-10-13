# Using RAMM-AI with an institutional or local model

RAMM-AI runs through OpenCode v2 with any model that supports tool calling,
  including models hosted by your institution and models running on your own
  computer.

## Institutionally hosted models

Most institutional deployments offer an OpenAI-compatible endpoint (for example
  vLLM or LiteLLM).
Ask your IT or research computing team, or check their documentation, for the
  endpoint address and the name of a model that supports tool calling.

1. Add the provider to OpenCode's own settings file,
  `~/.config/opencode/opencode.jsonc`, not to the `opencode.jsonc` in your study
  folder.
  It then works in every study folder, and the address stays out of folders you
  share:

```jsonc
{
  "providers": {
    "institution": {
      "name": "My institution",
      "package": "@opencode/ai/providers/openai-compatible",
      "settings": { "baseURL": "https://<host>/v1" },
      "models": { "<model-id>": { "name": "<display name>" } }
    }
  },
  "model": "institution/<model-id>"
}
```

2. Restart OpenCode's background service, so it reads the new settings:

```bash
opencode service restart
```

3. Give OpenCode your key, once:

```bash
opencode auth login institution
```

OpenCode keeps the key in its own data in your home folder, readable only by
  your user account but not encrypted.
- Use this only on your own computer, not a shared one.
- If your computer is lost or the key may have leaked, revoke the key yourself
  if your institution lets you, or ask them to revoke it.
- Check your institution's guidance on storing keys.

## Local models

Start Ollama and pull a model; OpenCode finds a running Ollama server by itself
  and lists its models under `/models`.

## What the model needs

The model must support tool calling, so it can read `inputs/input.md` and write
  the script.
`docs/tested-versions.md` lists the models we have tested.
