#!/usr/bin/env bash
# v2.3 plan §4.1: replay every stock input of the v2.2 pack under agent-tool-v3.2
# and harness v25, same teacher actions, same per-path cases. Nothing calls a teacher.
#
#   bench/distill/tools/v23/rerender_v32.sh
#   python3 bench/distill/tools/v23/compare_v32.py
#
# Inputs: the v2.1/v2.0 renders already replayed under agent-tool-v3.0
# (local/runs/distill/v21-v3/<name>/corpus, read_lines renamed) and the v2.2
# batches (local/runs/distill/v22/<batch>/corpus).
# Output: local/runs/distill/v2.3/stock/<name>/corpus/.
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"; cd "$repo"
A=local/runs/distill/v21-v3; B=local/runs/distill/v22; O=local/runs/distill/v2.3/stock
inputs=()
for n in main b21i b21j b21k b21l b21m b21n b21o b21p ref-v20 ref-v21 ref-b21i ref-b21l ref-b21n \
         v20app-qwen v20app-qwen-calc v20rec; do inputs+=("$n $A/$n/corpus"); done
for n in b22a b22b b22c b22c-q38 b22d b22e v21-redo v20-redo ref-v21-redo ref-v20-redo; do inputs+=("$n $B/$n/corpus"); done
mkdir -p "$O"
for item in "${inputs[@]}"; do
  read -r name src <<<"$item"
  out="$O/$name/corpus"
  if [ -f "$out/rows.jsonl" ]; then echo "skip $name (done)"; continue; fi
  rm -rf "$out"; mkdir -p "$out"
  cp "$src/script.jsonl" "$out/script.jsonl"
  cp -R "$src/cases" "$out/cases"
  source="$(python3 -c 'import ast,json,sys; m=json.loads(open(sys.argv[1]).readline())["meta"]; m=m if isinstance(m,dict) else ast.literal_eval(m); print(m["source"])' "$src/rows.jsonl")"
  local/bin/rwkv-cli-v23 agent-eval --script "$out/script.jsonl" --cases "$out/cases" --include-draft \
    --case-parallelism 32 --output "$out/run" --tool-catalog agent-tool-v3.2 --profile g1k-think --decision-max-tokens 4096 \
    --file-tools lines --max-steps 16 --max-tokens 4096 --strict-spec --trace-prompt-bytes -1 --harness app \
    > "$O/$name/render.log" 2>&1 || true
  local/bin/rwkv-lab-v23 corpus rows --run "$out/run" --script "$out/script.jsonl" --cases "$out/cases" \
    --source "$source" --out "$out/rows.jsonl" --rejects "$out/rejects.jsonl" --require-pass=false >> "$O/$name/render.log" 2>&1
  echo "$name: $(tail -1 "$O/$name/render.log")"
done
