#!/usr/bin/env bash
# Re-run only the cases a batch's teacher-k0 failed, once, into teacher-k1
# (cheaper than a full second pass; corpus paths then picks per case across
# both runs). Same overrides as run_teacher.sh (TEACHER_ENV_FILE, TEACHER_MODEL,
# REASONING_EFFORT, PARALLEL).
#   bench/distill/tools/v20/retry_failed.sh <batch>
set -euo pipefail
batch="${1:?batch}"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"; cd "$repo"
T="local/runs/distill/v20/$batch"
[ -e "$T/teacher-k1" ] && { echo "$T/teacher-k1 exists"; exit 1; }
rm -rf "$T/cases-retry"; mkdir -p "$T/cases-retry"
python3 - "$T" <<'PY'
import json, sys, os, shutil, glob
T = sys.argv[1]
failed = {c["id"] for c in json.load(open(T + "/teacher-k0/summary.json"))["cases"] if not c["passed"]}
for path in glob.glob(T + "/cases/*/*/case.json"):
    d = os.path.dirname(path)
    if os.path.basename(d) in failed:
        dst = os.path.join(T, "cases-retry", os.path.basename(os.path.dirname(d)), os.path.basename(d))
        shutil.copytree(d, dst)
print("retrying %d failed case(s)" % len(failed))
PY
source "${TEACHER_ENV_FILE:-$HOME/.llm_api_key.sh}"
local/bin/rwkv-cli-chat-v20 agent-eval --completion chat-completions --api-url "$API_BASE" --model "${TEACHER_MODEL:-$MODEL_NAME}" \
  --api-key-env API_KEY --chat-thinking enabled ${REASONING_EFFORT:+--chat-reasoning-effort "$REASONING_EFFORT"} \
  --temperature 0.3 --top-p 1 \
  --tool-catalog work-v2 --file-tools lines --max-steps 16 --max-tokens 4096 --decision-max-tokens 8192 \
  --case-parallelism "${PARALLEL:-12}" --case-timeout 30m --remote-batch-wait 0s \
  --cases "$T/cases-retry" --include-draft --output "$T/teacher-k1" > "$T/teacher-k1.log" 2>&1 || true
grep -h "cases passed" "$T/teacher-k1.log" || tail -3 "$T/teacher-k1.log"
