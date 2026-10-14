#!/usr/bin/env bash
# v2.0 after the teacher: pick one path per case (passing first; failing ones
# are kept so a judge fix re-judges them on replay), filter, and render
# per-step g1k-think rows against the same materialized cases the teacher saw.
#
#   bench/distill/tools/v20/render.sh <batch>
#
# Output under local/runs/distill/v20/<batch>/: paths.jsonl, paths-report.jsonl,
# script.jsonl, filter-report.json, corpus/{rows.jsonl,rejects.jsonl,run/}.
set -euo pipefail
batch="${1:?batch}"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"; cd "$repo"
T="local/runs/distill/v20/$batch"
runs=(); for d in "$T"/teacher-k*/; do [ -f "$d/trace.jsonl" ] && runs+=(--run "${d%/}"); done
local/bin/rwkv-lab-v20 corpus paths "${runs[@]}" --max-per-case 1 --include-failed --out "$T/paths.jsonl" --report "$T/paths-report.jsonl"
python3 bench/distill/tools/v20/filter.py --script "$T/paths.jsonl" --cases "$T/cases" \
  --out "$T/script.jsonl" --report "$T/filter-report.json"
local/bin/rwkv-lab-v20 corpus render --cases "$T/cases" --script "$T/script.jsonl" --out "$T/corpus" \
  --source "distill-$batch" --profile g1k-think --tool-catalog work-v2 --cli local/bin/rwkv-cli-v20
