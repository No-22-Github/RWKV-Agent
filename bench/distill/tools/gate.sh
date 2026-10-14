#!/usr/bin/env bash
# S2 gate for one version's cases: lint + verify (with sabotage).
#   bench/distill/tools/gate.sh v1.41            all cases of that version
#   bench/distill/tools/gate.sh v1.4 '*-80[0-3]?'  only ids matching the glob
set -euo pipefail
version="${1:?usage: gate.sh <version> [id-glob]}"
pattern="${2:-*}"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
lab="${RWKV_LAB:-$repo/local/bin/rwkv-lab}"   # v2.0: RWKV_LAB=local/bin/rwkv-lab-v20 (tool_policy)
tmp="$(mktemp -d)"
for dir in "$repo"/bench/distill/"$version"/cases/*/$pattern; do
  scenario="$(basename "$(dirname "$dir")")"
  mkdir -p "$tmp/$scenario" && cp -R "$dir" "$tmp/$scenario/"
done
"$lab" bank lint --cases "$tmp" --canary-prefix DISTILL-CANARY || true
"$lab" bank verify --cases "$tmp" --strict-shape 2>/dev/null | python3 -c '
import json, sys
r = json.load(sys.stdin)
print("verify", r["passed"], "/", r["total"])
for x in r["results"]:
    bad = [(c["check"], c.get("error"), (c.get("detail") or "")[:160]) for c in x["checks"] if not c["ok"]]
    if bad:
        print(x["case"], bad)'
