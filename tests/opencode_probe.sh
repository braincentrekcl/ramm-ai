#!/usr/bin/env bash
# Load the OpenCode template in a throwaway folder and check that OpenCode
# keeps every rule. A syntax error drops the whole file, and an invalid rule
# is dropped, both without an error (checked with OpenCode 2.0.24).
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
study="$(mktemp -d)"
cp "$repo_root/opencode/opencode.jsonc" "$study/"
cd "$study"
opencode api --standalone GET /api/config > config.json
python3 - "$repo_root/opencode/opencode.jsonc" config.json <<'PY'
import json, sys
template = json.loads("\n".join(
    line for line in open(sys.argv[1]) if not line.lstrip().startswith("//")))
loaded = [s for s in json.load(open(sys.argv[2])) if s.get("type") == "document"]
if not loaded:
    sys.exit("OpenCode did not load the template: check its syntax")
kept = loaded[0]["info"].get("permissions", [])
if len(kept) != len(template["permissions"]):
    sys.exit(f"OpenCode kept {len(kept)} of {len(template['permissions'])} rules: "
             "a rule has an invalid action or effect")
if loaded[0]["info"].get("skills") != template["skills"]:
    sys.exit("OpenCode dropped the skills setting")
print(f"OpenCode loads all {len(kept)} rules and the skills setting")
PY
