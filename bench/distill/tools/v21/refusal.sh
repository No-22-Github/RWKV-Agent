#!/usr/bin/env bash
# v2.1 refused-tool answers for one source batch (see build_refusal.py).
#   bench/distill/tools/v21/refusal.sh <run dir under local/runs/distill> <out name> [limit]
#   bench/distill/tools/v21/refusal.sh v20/qwen ref-v20 120
# Rows land in local/runs/distill/v21/<out name>/corpus/rows.jsonl.
set -euo pipefail
src="${1:?source batch}"; name="${2:?out name}"; limit="${3:-0}"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"; cd "$repo"
S="local/runs/distill/$src"; O="local/runs/distill/v21/$name"
rows="$S/corpus/rows.jsonl"; [ "$src" = v20/qwen ] && rows=local/runs/distill/v21/v20app-qwen/rows.jsonl
render() { local/bin/rwkv-lab-v21 corpus render --cases "$S/cases" --script "$1" --out "$2" --source "distill-v21-$name" \
  --profile g1k-think --tool-catalog agent-tool-v2.0 --cli local/bin/rwkv-cli-v21 "${@:3}" -- --harness app; }
python3 bench/distill/tools/v21/build_refusal.py prepare --batch "$src" --rows "$rows" --out "$O" --limit "$limit"
render "$O/probe.jsonl" "$O/probe-render" --keep-failing > "$O/probe-render.log" 2>&1 || true
source "${TEACHER_ENV_FILE:-$HOME/.llm_api_key.sh}"
python3 bench/distill/tools/v21/build_refusal.py teacher --out "$O" --parallel "${PARALLEL:-16}"
python3 bench/distill/tools/v21/filter.py --script "$O/script.jsonl" --cases "$S/cases" --out "$O/script-filtered.jsonl" --report "$O/filter-report.json"
render "$O/script-filtered.jsonl" "$O/corpus" > "$O/render.log" 2>&1 || true
tail -3 "$O/render.log"
