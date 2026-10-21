#!/usr/bin/env bash
# agent-tool-v3.1 M5 (docs/design/agent-tool-v3.md §2.12, §5): replay every v2.1 pack
# input under the agent-tool-v3.1 catalog, same teacher actions, same cases.
#
#   go build -o local/bin/rwkv-cli-v3 ./cmd/rwkv-cli && go build -o local/bin/rwkv-lab-v3 ./cmd/rwkv-lab
#   bench/distill/tools/v21/rerender_v3.sh
#   python3 bench/distill/tools/v21/compare_v3.py
#
# Output: local/runs/distill/v21-v3/<input>/corpus/. Nothing calls a teacher.
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"; cd "$repo"
V=local/runs/distill/v21; O=local/runs/distill/v21-v3
# <name> <render dir holding cases/ and script.jsonl>
inputs=(
  "main $V/main/corpus" "b21i $V/b21i/corpus" "b21j $V/b21j/corpus" "b21k $V/b21k/corpus"
  "b21l $V/b21l/corpus" "b21m $V/b21m/corpus" "b21n $V/b21n/corpus" "b21o $V/b21o/corpus"
  "b21p $V/b21p/corpus" "ref-v20 $V/ref-v20/corpus" "ref-v21 $V/ref-v21/corpus"
  "ref-b21i $V/ref-b21i/corpus" "ref-b21l $V/ref-b21l/corpus" "ref-b21n $V/ref-b21n/corpus"
  "v20app-qwen $V/v20app-qwen" "v20app-qwen-calc $V/v20app-qwen-calc" "v20rec $V/v20rec/corpus"
)
mkdir -p "$O"
for item in "${inputs[@]}"; do
  read -r name src <<<"$item"
  out="$O/$name/corpus"
  if [ -f "$out/rows.jsonl" ]; then echo "skip $name (done)"; continue; fi
  rm -rf "$out"; mkdir -p "$out"
  # The saved render dir already holds the per-path cases (cfg-31003--p1) the
  # first render resolved, so replay it directly: same flags as corpus render
  # (benchFlags), catalog agent-tool-v3.1, read_lines renamed to read_file.
  python3 - "$src/script.jsonl" "$out/script.jsonl" <<'PY'
import json, sys
src, dst = sys.argv[1:]
with open(src) as f, open(dst, "w") as g:
    for line in f:
        entry = json.loads(line)
        for output in entry.get("outputs", []):
            # agent-tool-v3.1 has no read_lines: rename it in the action and in the
            # teacher's reasoning that names it, so the row stays consistent.
            for field in ("text", "reasoning"):
                if isinstance(output.get(field), str):
                    output[field] = output[field].replace("read_lines", "read_file")
        g.write(json.dumps(entry, ensure_ascii=False) + "\n")
PY
  cp -R "$src/cases" "$out/cases"
  source="$(python3 -c 'import json,sys; print(json.loads(open(sys.argv[1]).readline())["meta"]["source"])' "$src/rows.jsonl")"
  local/bin/rwkv-cli-v3 agent-eval --script "$out/script.jsonl" --cases "$out/cases" --include-draft \
    --case-parallelism 32 --output "$out/run" --tool-catalog agent-tool-v3.1 --profile g1k-think --decision-max-tokens 4096 \
    --file-tools lines --max-steps 16 --max-tokens 4096 --strict-spec --trace-prompt-bytes -1 --harness app \
    > "$O/$name/render.log" 2>&1 || true
  local/bin/rwkv-lab-v3 corpus rows --run "$out/run" --script "$out/script.jsonl" --cases "$out/cases" \
    --source "$source" --out "$out/rows.jsonl" --rejects "$out/rejects.jsonl" --require-pass=false >> "$O/$name/render.log" 2>&1
  echo "$name: $(tail -1 "$O/$name/render.log")"
done
