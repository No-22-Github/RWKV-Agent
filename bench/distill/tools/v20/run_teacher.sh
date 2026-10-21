#!/usr/bin/env bash
# v2.0 teacher run for one batch: draw the tool directories, check
# contamination against every test bank, then run DeepSeek with thinking on
# every step and NO system suffix (the 1.x suffix leaked into the reasoning).
#
#   bench/distill/tools/v20/run_teacher.sh <batch> <id-glob> [k] [ids-file]
#   bench/distill/tools/v20/run_teacher.sh smoke '*' 1 local/runs/distill/v20/smoke-ids.txt
#   TEACHER_ENV_FILE=~/.commandcode_key.sh TEACHER_MODEL=<model> REASONING_EFFORT=max PARALLEL=16 run_teacher.sh ...   (optional overrides)
#
# Output: local/runs/distill/v20/<batch>/{cases,toolsets.jsonl,decontam.txt,teacher-k<i>}.
# Credentials: ~/.llm_api_key.sh (API_BASE / API_KEY / MODEL_NAME).
# Needs local/bin/rwkv-cli-chat-v20 (go build -tags chatcompletions) and
# local/bin/rwkv-lab-v20, built from a tree with tool_policy support.
set -euo pipefail
batch="${1:?batch}"; glob="${2:?id glob}"; k="${3:-1}"; ids="${4:-}"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"; cd "$repo"
T="local/runs/distill/v20/$batch"
mkdir -p "$T"
idarg=(); [ -n "$ids" ] && idarg=(--ids-file "$ids")
python3 bench/distill/tools/v20/materialize.py --cases bench/distill/v2.0/cases --out "$T/cases" \
  --ids-glob "$glob" "${idarg[@]}"
echo "cases: $(find "$T/cases" -name case.json | wc -l)"
: > "$T/decontam.txt"
for t in bench/workbank/cases bench/workbank/cases-shelved bench/holdout/p13 bench/distill/v1/cases-shelved \
         bench/bashprobe/cases bench/bashprobe/cases-b14 bench/bashprobe/reserve \
         bench/weatherprobe/cases bench/weatherprobe/cases-b14 bench/weatherprobe/reserve; do
  echo "== $t" >> "$T/decontam.txt"
  local/bin/rwkv-lab-v20 corpus decontam --test "$t" --candidates "$T/cases" 2>&1 | grep -E "flagged|~" >> "$T/decontam.txt" || true
done
cat "$T/decontam.txt"
# Anything flagged against any test bank is dropped before the teacher sees it
# (1.x rule: when in doubt, the test bank wins).
for id in $(grep "~" "$T/decontam.txt" | awk '{print $1}' | sort -u); do
  rm -rf "$T"/cases/*/"$id"; echo "$id" >> "$T/decontam-dropped.txt"
done
echo "cases after decontam: $(find "$T/cases" -name case.json | wc -l)"
source "${TEACHER_ENV_FILE:-$HOME/.llm_api_key.sh}"   # must export API_BASE, API_KEY (and MODEL_NAME unless TEACHER_MODEL is set)
for i in $(seq 0 $((k - 1))); do
  local/bin/rwkv-cli-chat-v20 agent-eval --completion chat-completions --api-url "$API_BASE" --model "${TEACHER_MODEL:-$MODEL_NAME}" \
    --api-key-env API_KEY --chat-thinking enabled ${REASONING_EFFORT:+--chat-reasoning-effort "$REASONING_EFFORT"} \
    --temperature 0.3 --top-p 1 \
    --tool-catalog agent-tool-v2.0 --file-tools lines --max-steps 16 --max-tokens 4096 --decision-max-tokens 8192 \
    --case-parallelism "${PARALLEL:-12}" --case-timeout 30m --remote-batch-wait 0s \
    --cases "$T/cases" --include-draft --output "$T/teacher-k$i" > "$T/teacher-k$i.log" 2>&1 || true
  grep -h "cases passed" "$T/teacher-k$i.log" || tail -3 "$T/teacher-k$i.log"
done
