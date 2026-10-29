#!/usr/bin/env bash
# v2.3 (agent-tool-v3.2) after the teacher: pick one path per case (passing first; failing ones
# are kept so a judge fix re-judges them on replay), filter, and render
# per-step g1k-think rows against the same materialized cases the teacher saw.
#
#   bench/distill/tools/v23/render.sh <batch> [exclude-ids-file]
#
# exclude-ids-file: cases rerun in another batch (e.g. qwen-calc after the
# precision fix); this batch's paths for them are dropped as superseded.
#
# Output under local/runs/distill/v2.3/<batch>/: paths.jsonl, paths-report.jsonl,
# script.jsonl, filter-report.json, corpus/{rows.jsonl,rejects.jsonl,run/}.
set -euo pipefail
batch="${1:?batch}"; exclude="${2:-}"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"; cd "$repo"
T="local/runs/distill/v2.3/$batch"
runs=(); for d in "$T"/teacher-k*/; do [ -f "$d/trace.jsonl" ] && runs+=(--run "${d%/}"); done
local/bin/rwkv-lab-v23 corpus paths "${runs[@]}" --max-per-case 1 --include-failed --keep-recovery --out "$T/paths.jsonl" --report "$T/paths-report.jsonl"
python3 bench/distill/tools/v23/filter.py --script "$T/paths.jsonl" --cases "$T/cases" \
  --out "$T/script.jsonl" --report "$T/filter-report.json" ${exclude:+--exclude-ids "$exclude"}
local/bin/rwkv-lab-v23 corpus render --cases "$T/cases" --script "$T/script.jsonl" --out "$T/corpus" \
  --source "distill-$batch" --profile g1k-think --tool-catalog agent-tool-v3.2 --cli local/bin/rwkv-cli-v23 -- --harness app
