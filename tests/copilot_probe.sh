#!/usr/bin/env bash
# Install the plugin into a throwaway Copilot CLI home and check that it is
# enabled and brings every skill in skills/. Needs no login (checked with
# Copilot CLI 1.0.93).
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
probe="$(mktemp -d)"
trap 'rm -rf "$probe"' EXIT
export COPILOT_HOME="$probe/home"
mkdir -p "$COPILOT_HOME"
copilot plugin marketplace add "$repo_root"
output="$(copilot plugin install ramm@ramm-ai)"
echo "$output"
copilot plugin list --json | python3 -c '
import json, sys
if not any(p["name"] == "ramm" and p["enabled"] for p in json.load(sys.stdin)):
    sys.exit("Copilot does not list the ramm plugin as enabled")'
expected=$(find "$repo_root/skills" -name SKILL.md | wc -l | tr -d " ")
installed=$(sed -nE 's/.*Installed ([0-9]+) skills?.*/\1/p' <<<"$output")
if [[ "$installed" != "$expected" ]]; then
  echo "Copilot installed ${installed:-no} skills; skills/ has $expected" >&2
  exit 1
fi
echo "Copilot installs ramm with all $expected skills"
