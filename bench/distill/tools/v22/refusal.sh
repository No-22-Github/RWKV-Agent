#!/usr/bin/env bash
# v2.2 refused-tool answers on work-v3 (tools/v21/build_refusal.py, same method
# as v2.1), built from one v2.2 batch's passing paths. Used 2026-10-20 to
# rebuild the refusals the work-v3 replay dropped, from the re-teachered paths.
#   bench/distill/tools/v22/refusal.sh <source batch> <out name> [ids-file]
#   bench/distill/tools/v22/refusal.sh v21-redo ref-v21-redo ids.txt
# Rows land in local/runs/distill/v22/<out name>/corpus/rows.jsonl.
set -euo pipefail
src="${1:?source batch}"; name="${2:?out name}"; ids="${3:-}"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"; cd "$repo"
S="local/runs/distill/v22/$src"; O="local/runs/distill/v22/$name"
render() { local/bin/rwkv-lab-v3 corpus render --cases "$S/cases" --script "$1" --out "$2" --source "distill-v22-$name" \
  --profile g1k-think --tool-catalog work-v3 --cli local/bin/rwkv-cli-v3 "${@:3}" -- --harness app; }
python3 bench/distill/tools/v21/build_refusal.py prepare --batch "v22/$src" --rows "$S/corpus/rows.jsonl" --out "$O" \
  ${ids:+--ids-file "$ids"}
render "$O/probe.jsonl" "$O/probe-render" --keep-failing > "$O/probe-render.log" 2>&1 || true
source "${TEACHER_ENV_FILE:-$HOME/.llm_api_key.sh}"
python3 bench/distill/tools/v21/build_refusal.py teacher --out "$O" --parallel "${PARALLEL:-8}"
python3 bench/distill/tools/v22/filter.py --script "$O/script.jsonl" --cases "$S/cases" --out "$O/script-filtered.jsonl" --report "$O/filter-report.json"
render "$O/script-filtered.jsonl" "$O/corpus" > "$O/render.log" 2>&1 || true
tail -3 "$O/render.log"
