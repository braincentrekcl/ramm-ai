#!/usr/bin/env bash
# Load the OpenCode template in a throwaway folder and check that OpenCode
# keeps every rule and finds both skills (checked with OpenCode 2.0.24).
# A syntax error drops the whole file and an invalid rule is dropped, both
# without an error, so the rules are counted.
# OpenCode runs under a throwaway home on its own port, so the probe never
# touches the user's own OpenCode service or settings.
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
probe="$(mktemp -d)"
export HOME="$probe/home"
mkdir -p "$HOME" "$probe/rules" "$probe/skills"
trap 'opencode service stop > /dev/null 2>&1 || true; rm -rf "$probe"' EXIT

cp "$repo_root/opencode/opencode.jsonc" "$probe/rules/"
(cd "$probe/rules" && opencode api --standalone GET /api/config) > "$probe/config.json"
python3 - "$repo_root/opencode/opencode.jsonc" "$probe/config.json" <<'PY'
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
# The first requests for a new folder only start OpenCode there, so retry, and
# treat a failed or non-JSON answer as "not yet".
sed "s|/path/to/ramm-ai/skills|$repo_root/skills|" \
  "$repo_root/opencode/opencode.jsonc" > "$probe/skills/opencode.jsonc"
port="$(python3 -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])')"
opencode service set port "$port" > /dev/null
opencode service start > /dev/null
skills=""
for attempt in $(seq 1 10); do
  skills="$(opencode api GET "/api/skill?location%5Bdirectory%5D=$probe/skills" 2> /dev/null |
    python3 -c '
import json, sys
try:
    print(" ".join(s["id"] for s in json.load(sys.stdin)["data"]))
except (ValueError, KeyError, TypeError):
    pass' || true)"
  if [[ " $skills " == *" ramm "* && " $skills " == *" reproduce "* ]]; then
    echo "OpenCode loads the ramm and reproduce skills"
    exit 0
  fi
  sleep 3
done
echo "OpenCode did not list the ramm and reproduce skills; it listed: ${skills:-nothing}" >&2
exit 1
