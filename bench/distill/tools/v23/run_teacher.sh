#!/usr/bin/env bash
# v2.3 teacher run for one batch (agent-tool-v3.2 catalog): draw the tool directories, check
# contamination against every test bank (exam included), then run the teacher
# (Qwen3.7-Flash) with thinking on every step, NO system suffix, and the App
# harness (--harness app: App system prompt and tool order, staged files,
# duplicate/same-tool rescue on as in the App).
#
#   bench/distill/tools/v23/run_teacher.sh <batch> <id-glob> [k] [ids-file]
#   bench/distill/tools/v23/run_teacher.sh b22a 'web-34*'
#   CASES=bench/distill/v2.1/cases bench/distill/tools/v23/run_teacher.sh v21-redo '*' 1 local/runs/distill/v21-v3/reteacher-ids/v2.1.txt
#   TEACHER_ENV_FILE=~/.commandcode_key.sh TEACHER_MODEL=<model> REASONING_EFFORT=max PARALLEL=16 run_teacher.sh ...   (optional overrides)
#   SYSTEM_SUFFIX=bench/distill/v2.2/teacher/b22c-suffix.txt run_teacher.sh ...   (teacher-only instruction; never reaches rendered rows)
#
# Output: local/runs/distill/v2.3/<batch>/{cases,toolsets.jsonl,decontam.txt,teacher-k<i>}.
# Credentials: TEACHER_ENV_FILE (default ~/.commandcode_key.sh), KEY_SLOT (1 or 2) (API_BASE / API_KEY / MODEL_NAME).
# CASES picks the case tree (default bench/distill/v2.3/cases). Needs
# local/bin/rwkv-cli-chat-v23 (go build -tags chatcompletions -o local/bin/rwkv-cli-chat-v23 ./cmd/rwkv-cli)
# and local/bin/rwkv-lab-v23, built from a tree with agent-tool-v3.2 (25d1f2f0 or later).
set -euo pipefail
batch="${1:?batch}"; glob="${2:?id glob}"; k="${3:-1}"; ids="${4:-}"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"; cd "$repo"
T="local/runs/distill/v2.3/$batch"
mkdir -p "$T"
idarg=(); [ -n "$ids" ] && idarg=(--ids-file "$ids")
python3 bench/distill/tools/v23/materialize.py --cases "${CASES:-bench/distill/v2.3/cases}" --out "$T/cases" \
  --ids-glob "$glob" "${idarg[@]}"
echo "cases: $(find "$T/cases" -name case.json | wc -l)"
: > "$T/decontam.txt"
for t in bench/exam/cases bench/workbank/cases bench/workbank/cases-shelved bench/holdout/p13 bench/distill/v1/cases-shelved \
         bench/bashprobe/cases bench/bashprobe/cases-b14 bench/bashprobe/reserve \
         bench/weatherprobe/cases bench/weatherprobe/cases-b14 bench/weatherprobe/reserve; do
  echo "== $t" >> "$T/decontam.txt"
  local/bin/rwkv-lab-v23 corpus decontam --test "$t" --candidates "$T/cases" 2>&1 | grep -E "flagged|~" >> "$T/decontam.txt" || true
done
cat "$T/decontam.txt"
# Anything flagged against any test bank is dropped before the teacher sees it
# (1.x rule: when in doubt, the test bank wins).
for id in $(grep "~" "$T/decontam.txt" | awk '{print $1}' | sort -u); do
  rm -rf "$T"/cases/*/"$id"; echo "$id" >> "$T/decontam-dropped.txt"
done
echo "cases after decontam: $(find "$T/cases" -name case.json | wc -l)"
source "${TEACHER_ENV_FILE:-$HOME/.commandcode_key.sh}"   # API_BASE, API_KEY (MODEL_NAME unless TEACHER_MODEL is set)
# ~/.commandcode_key.sh also holds CC_API_KEY_1/CC_API_KEY_2: key 1 first, KEY_SLOT=2 once key 1 is saturated.
slot="CC_API_KEY_${KEY_SLOT:-1}"; [ -n "${!slot:-}" ] && export API_KEY="${!slot}"
for i in $(seq 0 $((k - 1))); do
  local/bin/rwkv-cli-chat-v23 agent-eval --completion chat-completions --api-url "$API_BASE" --model "${TEACHER_MODEL:-$MODEL_NAME}" \
    --api-key-env API_KEY --chat-thinking enabled ${REASONING_EFFORT:+--chat-reasoning-effort "$REASONING_EFFORT"} ${SYSTEM_SUFFIX:+--chat-system-suffix "$SYSTEM_SUFFIX"} \
    --temperature 0.3 --top-p 1 \
    --harness app --tool-catalog agent-tool-v3.2 --file-tools lines --max-steps 16 --max-tokens 4096 --decision-max-tokens 8192 \
    --case-parallelism "${PARALLEL:-12}" --case-timeout 40m --remote-batch-wait 0s \
    --cases "$T/cases" --include-draft --output "$T/teacher-k$i" > "$T/teacher-k$i.log" 2>&1 || true
  grep -h "cases passed" "$T/teacher-k$i.log" || tail -3 "$T/teacher-k$i.log"
done
