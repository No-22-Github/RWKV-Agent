#!/usr/bin/env bash
# Re-run only the cases no earlier teacher-k* run of a batch passed, into teacher-k$K (K=1 default; v2.3: K=2 TEMP=0.6 for the third pass)
# (cheaper than a full second pass; corpus paths then picks per case across
# both runs). Same overrides as run_teacher.sh (TEACHER_ENV_FILE, TEACHER_MODEL,
# REASONING_EFFORT, PARALLEL).
#   bench/distill/tools/v23/retry_failed.sh <batch>
set -euo pipefail
batch="${1:?batch}"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"; cd "$repo"
T="local/runs/distill/v2.3/$batch"
K="${K:-1}"
[ -e "$T/teacher-k$K" ] && { echo "$T/teacher-k$K exists"; exit 1; }
rm -rf "$T/cases-retry"; mkdir -p "$T/cases-retry"
python3 - "$T" <<'PY'
import json, sys, os, shutil, glob
T = sys.argv[1]
passed = set()
for summ in glob.glob(T + "/teacher-k*/summary.json"):
    passed |= {c["id"] for c in json.load(open(summ))["cases"] if c["passed"]}
failed = {c["id"] for c in json.load(open(T + "/teacher-k0/summary.json"))["cases"]} - passed
for path in glob.glob(T + "/cases/*/*/case.json"):
    d = os.path.dirname(path)
    if os.path.basename(d) in failed:
        dst = os.path.join(T, "cases-retry", os.path.basename(os.path.dirname(d)), os.path.basename(d))
        shutil.copytree(d, dst)
print("retrying %d failed case(s)" % len(failed))
PY
source "${TEACHER_ENV_FILE:-$HOME/.commandcode_key.sh}"   # API_BASE, API_KEY (MODEL_NAME unless TEACHER_MODEL is set)
# ~/.commandcode_key.sh also holds CC_API_KEY_1/CC_API_KEY_2: key 1 first, KEY_SLOT=2 once key 1 is saturated.
slot="CC_API_KEY_${KEY_SLOT:-1}"; [ -n "${!slot:-}" ] && export API_KEY="${!slot}"
local/bin/rwkv-cli-chat-v23 agent-eval --completion chat-completions --api-url "$API_BASE" --model "${TEACHER_MODEL:-$MODEL_NAME}" \
  --api-key-env API_KEY --chat-thinking enabled ${REASONING_EFFORT:+--chat-reasoning-effort "$REASONING_EFFORT"} \
  --temperature "${TEMP:-0.3}" --top-p 1 \
  --harness app --tool-catalog agent-tool-v3.2 --file-tools lines --max-steps 16 --max-tokens 4096 --decision-max-tokens 8192 \
  --case-parallelism "${PARALLEL:-12}" --case-timeout 40m --remote-batch-wait 0s \
  --cases "$T/cases-retry" --include-draft --output "$T/teacher-k$K" > "$T/teacher-k$K.log" 2>&1 || true
grep -h "cases passed" "$T/teacher-k$K.log" || tail -3 "$T/teacher-k$K.log"
