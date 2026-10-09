#!/usr/bin/env bash
# Install the plugin into a throwaway Copilot CLI home and check that it
# brings both skills. Needs no login (checked with Copilot CLI 1.0.93).
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
export COPILOT_HOME="$(mktemp -d)/home"
mkdir -p "$COPILOT_HOME"
copilot plugin marketplace add "$repo_root"
output="$(copilot plugin install ramm@ramm-ai)"
echo "$output"
if ! grep -q "Installed 2 skills" <<<"$output"; then
  echo "Copilot did not install both skills (ramm and reproduce)" >&2
  exit 1
fi
echo "Copilot installs ramm with both skills"
