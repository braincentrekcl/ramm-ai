# Installing RAMM-AI

## From the command line

| Agent | Install | Start RAMM-AI | Start reproduce |
|---|---|---|---|
| Claude Code | `claude plugin marketplace add braincentrekcl/ramm-ai`, then `claude plugin install ramm@ramm-ai` | `/ramm:ramm` | `/ramm:reproduce` |
| Codex | `codex plugin marketplace add braincentrekcl/ramm-ai`, then `codex plugin add ramm@ramm-ai` | `$ramm:ramm` | `$ramm:reproduce` |
| GitHub Copilot (CLI and VS Code) | `copilot plugin marketplace add braincentrekcl/ramm-ai`, then `copilot plugin install ramm@ramm-ai` | `/ramm` | `/reproduce` |
| OpenCode v2 | Download this repository, then copy `opencode/opencode.jsonc` into your study folder and set the path to this repository's `skills` folder in it | `@ramm` | `@reproduce` |

## From an app, without the command line

Each app has its own steps for plugins; follow its documentation, using these
  values:

- **Marketplace** (add this first): `braincentrekcl/ramm-ai`, or
  `https://github.com/braincentrekcl/ramm-ai`
- **Plugin** (then install this): `ramm`

| App | Its documentation |
|---|---|
| Claude desktop app (Code tab) and Claude Code in VS Code | [Install and manage plugins](https://code.claude.com/docs/en/plugins/install): "Add a marketplace", then "Install a plugin" |
| GitHub Copilot app | [Customizing the GitHub Copilot app](https://docs.github.com/en/copilot/how-tos/github-copilot-app/customize-github-copilot-app): add the marketplace from the Plugins view, then install |
| GitHub Copilot in VS Code | [Agent plugins in VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-plugins): add the marketplace to `chat.plugins.marketplaces`, or run **Chat: Install Plugin From Source** with the GitHub address |
| Codex app | [Plugins](https://learn.chatgpt.com/docs/plugins): the app installs from OpenAI's and your workspace's plugin lists, so ask your workspace admin to import the marketplace, or use the command line above once |

## OpenCode notes

OpenCode: RAMM-AI supports OpenCode v2 only (`brew install
  anomalyco/tap/opencode-v2` or `npm install -g @opencode/cli`).
OpenCode cannot currently use a GitHub Copilot Free or Student plan: it lists
  no models for them ([anomalyco/opencode#34644](https://github.com/anomalyco/opencode/issues/34644)).
With those plans, use the GitHub Copilot route instead.
OpenCode's free models do not work while the template denies shell commands
  ([anomalyco/opencode#51241](https://github.com/anomalyco/opencode/issues/51241)).
To use one, change `deny` to `ask` on the shell line, keep your data out of the
  study folder as on the other agents, and decline any command that would read
  your data.
Free models may keep or learn from what you send, so check their terms; see
  [What the AI assistant can see and change](privacy-and-safety.md).
For institutionally hosted or local models, see
  [institutional-and-local-models.md](institutional-and-local-models.md).
