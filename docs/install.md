# Installing RAMM-AI

## First, install an agent

Use the agent's desktop app or its terminal version.
Its website will not work, because it cannot open files on your computer.
If you have never used a terminal, use the desktop app.

| Agent | Desktop app | Terminal |
|---|---|---|
| Claude Code | [Claude desktop app](https://code.claude.com/docs/en/desktop) (Code tab) | [Quickstart](https://code.claude.com/docs/en/quickstart) |
| OpenAI Codex | [ChatGPT desktop app](https://learn.chatgpt.com/docs/app) (Codex) | [Codex CLI](https://learn.chatgpt.com/docs/codex/cli) |
| GitHub Copilot | [GitHub Copilot app](https://docs.github.com/en/copilot/get-started/quickstart-copilot-app) | [Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli) |
| OpenCode v2 | [OpenCode Desktop](https://opencode.ai/v2/docs/#desktop) | [OpenCode](https://opencode.ai/v2/docs/) |

## Second, install RAMM-AI in your agent

Follow the steps for how you use your agent: in a terminal, or in its desktop
  app.

### From the command line

| Agent | Install |
|---|---|
| Claude Code | `claude plugin marketplace add braincentrekcl/ramm-ai`, then `claude plugin install ramm@ramm-ai` |
| OpenAI Codex | `codex plugin marketplace add braincentrekcl/ramm-ai`, then `codex plugin add ramm@ramm-ai` |
| GitHub Copilot (CLI and VS Code) | `copilot plugin marketplace add braincentrekcl/ramm-ai`, then `copilot plugin install ramm@ramm-ai` |
| OpenCode v2 | See the [OpenCode notes](#opencode) below |

### From an app, without the command line

Each app has its own steps for plugins; follow its documentation below.
When it asks for a marketplace, add RAMM-AI's: `braincentrekcl/ramm-ai` (some
  apps want the full address, `https://github.com/braincentrekcl/ramm-ai`).
Then install the plugin called `ramm` from it.

| App | Its documentation |
|---|---|
| Claude desktop app (Code tab) and Claude Code in VS Code | [Install and manage plugins](https://code.claude.com/docs/en/plugins/install): "Add a marketplace", then "Install a plugin" |
| GitHub Copilot app | [Customizing the GitHub Copilot app](https://docs.github.com/en/copilot/how-tos/github-copilot-app/customize-github-copilot-app): add the marketplace from the Plugins view, then install |
| GitHub Copilot in VS Code | [Agent plugins in VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-plugins): add the marketplace to `chat.plugins.marketplaces`, or run **Chat: Install Plugin From Source** with the GitHub address |
| ChatGPT desktop app (Codex) | [Plugins](https://learn.chatgpt.com/docs/plugins): in **Customize**, open **Plugins**, then the **Personal** tab, and add a plugin marketplace with RAMM-AI's address as the source (leave the other fields empty) |

## Agent-specific notes

### Claude Code

RAMM-AI reads some of its own files in the installed plugin:

- before writing the scripts, `skills/ramm/references/prepare.md` and `skills/ramm/references/script.md`;
- before writing the environment files, `skills/reproduce/references/container.md` or `skills/reproduce/references/renv.md`.

The plugin is outside your study folder, so Claude Code asks you before RAMM-AI reads these files ([Working directories](https://code.claude.com/docs/en/permissions#working-directories)).
We recommend that you allow it.
These files are RAMM-AI's own instructions, and they hold none of your data.
Without them, RAMM-AI writes the scripts without its tested patterns, and reproduce writes the environment files without its templates.
RAMM-AI never needs to read any other file outside your study folder, so you can refuse any other request.

### OpenCode

- **Use OpenCode version 2.**
  Version 1 reads permissions in a different format, so the template would not
  protect your data.
  To install version 2 in a terminal, run `brew install anomalyco/tap/opencode-v2`
  or `npm install -g @opencode/cli`, or follow the
  [OpenCode docs](https://opencode.ai/v2/docs/).
- **We provide a recommended template**, as part of the repository you downloaded or [here](https://github.com/braincentrekcl/ramm-ai/raw/main/opencode/opencode.jsonc).
  To use it:

    1. [Download this repository](https://github.com/braincentrekcl/ramm-ai/archive/refs/heads/main.zip) and unzip it.
    2. Copy `opencode/opencode.jsonc` from it into your study folder.
    3. Open the copy in a text editor and replace `/path/to/ramm-ai` (it appears
       three times) with the full path of the unzipped folder, for example
       `/Users/yourname/Documents/ramm-ai-main`.

    You can change the template for your study if you need to.
    It should stop OpenCode reading your data, and stop it changing files outside
    `code/` and `envs/`.
    To be completely sure nothing leaks, also keep your data out of the study
    folder until you run the script, as
    [What the AI assistant can see and change](privacy-and-safety.md) explains.

- **The template works for the command line and the desktop app.**
  In the desktop app, it turns off the built-in browser, which could otherwise
  send a file from your study folder to a website without checking the
  template's rules.
- **GitHub Copilot Free or Student plans need OpenCode 2.2.7 or later.**
  Earlier versions show no models for these plans
  ([anomalyco/opencode#34644](https://github.com/anomalyco/opencode/issues/34644)).
- **OpenCode's free models do not work while the template blocks shell
  commands**
  ([anomalyco/opencode#51241](https://github.com/anomalyco/opencode/issues/51241)).
  To use one, open `opencode.jsonc` in your study folder and change `deny` to
  `ask` on the `shell` line.
  OpenCode will then ask you before it runs any command: refuse any command
  that would read your data.
- **Some free models keep what you send, or use it for training.**
  OpenCode's [list of free models](https://opencode.ai/docs/zen) says which;
  check it before you choose one.
  See also [What the AI assistant can see and change](privacy-and-safety.md).
- For models hosted by your institution or on your own computer, see
  [Institutional and local models](institutional-and-local-models.md).
