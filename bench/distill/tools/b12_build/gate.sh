#!/usr/bin/env bash
# S2 gate for b12 pilot cases: lint + verify (with sabotage) on the 9xxx cases only.
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
tmp="$(mktemp -d)"
for dir in "$repo"/bench/distill/cases/*/*-9[0-9][0-9][0-9]; do
  scenario="$(basename "$(dirname "$dir")")"
  mkdir -p "$tmp/$scenario" && cp -R "$dir" "$tmp/$scenario/"
done
"$repo/local/bin/rwkv-lab" bank lint --cases "$tmp" --canary-prefix DISTILL-CANARY || true
"$repo/local/bin/rwkv-lab" bank verify --cases "$tmp" --strict-shape 2>/dev/null | python3 -c '
import json, sys
r = json.load(sys.stdin)
print("verify", r["passed"], "/", r["total"])
for x in r["results"]:
    bad = [(c["check"], c.get("error"), (c.get("detail") or "")[:160]) for c in x["checks"] if not c["ok"]]
    if bad:
        print(x["case"], bad)'
