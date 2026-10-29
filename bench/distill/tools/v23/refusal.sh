#!/usr/bin/env bash
# v2.3 refused-tool answers on agent-tool-v3.2 (tools/v21/build_refusal.py, same method
# as v2.1), built from one batch's passing paths (SRC_DIR/SRC_BATCH point at stock inputs).
#   bench/distill/tools/v23/refusal.sh <source batch> <out name> [ids-file]
#   bench/distill/tools/v23/refusal.sh v21-redo ref-v21-redo ids.txt
# Rows land in local/runs/distill/v2.3/<out name>/corpus/rows.jsonl.
set -euo pipefail
src="${1:?source batch}"; name="${2:?out name}"; ids="${3:-}"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"; cd "$repo"
S="${SRC_DIR:-local/runs/distill/v2.3/$src}"; O="local/runs/distill/v2.3/$name"
render() { local/bin/rwkv-lab-v23 corpus render --cases "$S/cases" --script "$1" --out "$2" --source "distill-v23-$name" \
  --profile g1k-think --tool-catalog agent-tool-v3.2 --cli local/bin/rwkv-cli-v23 "${@:3}" -- --harness app; }
python3 bench/distill/tools/v21/build_refusal.py prepare --batch "${SRC_BATCH:-v2.3/$src}" --rows "$S/corpus/rows.jsonl" --out "$O" \
  ${ids:+--ids-file "$ids"}
render "$O/probe.jsonl" "$O/probe-render" --keep-failing > "$O/probe-render.log" 2>&1 || true
source "${TEACHER_ENV_FILE:-$HOME/.commandcode_key.sh}"
slot="CC_API_KEY_${KEY_SLOT:-1}"; [ -n "${!slot:-}" ] && export API_KEY="${!slot}"
python3 bench/distill/tools/v21/build_refusal.py teacher --out "$O" --parallel "${PARALLEL:-8}"
python3 bench/distill/tools/v23/filter.py --script "$O/script.jsonl" --cases "$S/cases" --out "$O/script-filtered.jsonl" --report "$O/filter-report.json"
render "$O/script-filtered.jsonl" "$O/corpus" > "$O/render.log" 2>&1 || true
tail -3 "$O/render.log"
