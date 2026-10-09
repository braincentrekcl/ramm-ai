#!/usr/bin/env bash
# Load the OpenCode template in a throwaway folder and check that OpenCode
# keeps every rule and finds both skills. A syntax error drops the whole file, and an invalid rule
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

# With the skills path set to this repository, OpenCode must list both skills.
# The first request for a new folder only starts OpenCode there, so retry.
skills_study="$(mktemp -d)"
sed "s|/path/to/ramm-ai/skills|$repo_root/skills|" \
  "$repo_root/opencode/opencode.jsonc" > "$skills_study/opencode.jsonc"
opencode service start > /dev/null
for attempt in 1 2 3 4 5 6 7 8 9 10; do
  skills="$(opencode api GET "/api/skill?location%5Bdirectory%5D=$skills_study" |
    python3 -c 'import json, sys; print(" ".join(s["id"] for s in json.load(sys.stdin)["data"]))')"
  if [[ " $skills " == *" ramm "* && " $skills " == *" reproduce "* ]]; then
    echo "OpenCode loads the ramm and reproduce skills"
    exit 0
  fi
  sleep 3
done
echo "OpenCode did not list the ramm and reproduce skills; it listed: $skills" >&2
exit 1
