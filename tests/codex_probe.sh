#!/usr/bin/env bash
# Install the plugin into a throwaway Codex home and check that the model
# sees both skills. Needs no login (checked with codex-cli 0.160.1).
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
probe="$(mktemp -d)"
export CODEX_HOME="$probe/home"
mkdir -p "$CODEX_HOME" "$probe/work"
codex plugin marketplace add "$repo_root"
codex plugin add ramm@ramm-ai
prompt="$(cd "$probe/work" && codex debug prompt-input hi)"
for skill in "ramm:ramm:" "ramm:reproduce:"; do
  if ! grep -q -- "$skill" <<<"$prompt"; then
    echo "Codex does not list the skill ${skill%:}" >&2
    exit 1
  fi
done
echo "Codex lists ramm:ramm and ramm:reproduce"
