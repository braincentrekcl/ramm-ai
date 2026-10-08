# Installing RAMM-AI

## From the command line

| Agent | Install | Start RAMM-AI | Start reproduce |
|---|---|---|---|
| Claude Code | `claude plugin marketplace add braincentrekcl/ramm-ai`, then `claude plugin install ramm@ramm-ai` | `/ramm:ramm` | `/ramm:reproduce` |
| Codex | `codex plugin marketplace add braincentrekcl/ramm-ai`, then `codex plugin add ramm@ramm-ai` | `$ramm:ramm` | `$ramm:reproduce` |
| GitHub Copilot (CLI and VS Code) | `copilot plugin marketplace add braincentrekcl/ramm-ai`, then `copilot plugin install ramm@ramm-ai` | `/ramm` | `/reproduce` |
| OpenCode v2 | Download this repository, then copy `opencode/opencode.jsonc` into your study folder and set the path to this repository's `skills` folder in it | `@ramm` | `@reproduce` |

## From an app, without the command line

These steps come from each vendor's documentation (checked 2026-10-08); we have
  not yet tried them by hand, so tell us if a step has changed.

### Claude desktop app (Code tab)

1. Open a local session in your study folder.
2. Click the **+** button next to the prompt box, select **Plugins**, then
  **Add plugin**.
3. Find `ramm`, select it, and choose a scope (your user account is simplest).

The plugin browser lists plugins from marketplaces you have already added, and
  the desktop app's documentation gives no button for adding a new one.
If `ramm` is not listed, add the RAMM-AI marketplace once with the first
  command in the table above (or from the Claude Code panel in VS Code, below);
  the desktop app, the command line and VS Code share the same plugins.

### Claude Code in VS Code

1. In the Claude Code panel, type `/plugins` to open **Manage plugins**.
2. On the **Marketplaces** tab, add `braincentrekcl/ramm-ai`.
3. On the **Plugins** tab, search for `ramm`, click **Install** and choose a
  scope.

### Codex app

The Codex app's **Plugins** page lists plugins from OpenAI, your workspace and
  your own account; its documentation gives no way to add a marketplace from a
  GitHub repository.
Use the Codex command in the table above, or ask your workspace admin to import
  the `braincentrekcl/ramm-ai` marketplace for your team.

### GitHub Copilot in VS Code

1. Open the Command Palette and run **Chat: Install Plugin From Source**.
2. Enter `https://github.com/braincentrekcl/ramm-ai` and confirm that you trust
  it.

Or add the marketplace in your VS Code settings (`settings.json`):

```json
"chat.plugins.marketplaces": ["braincentrekcl/ramm-ai"]
```

then open the Chat view, select the cog, open **Agent Customizations**, choose
  **Plugins**, and install `ramm`.
Your organisation may need to turn on `chat.plugins.enabled` first.

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
Free models may keep or learn from what you send, so check their terms.
For institutionally hosted or local models, see
  [institutional-and-local-models.md](institutional-and-local-models.md).
