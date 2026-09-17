#!/bin/bash
# workbank closeout run matrix driver — sequential, one endpoint load profile.
set -u
cd /Users/no22/Projects/RWKV-Agent

CLI=./build/rwkv-cli
CHAT=./build/rwkv-cli-chat
RWKV_URL=http://100.64.0.1:18222/v1
MODEL=rwkv-g1k-7b-temp-3601
BASE_PROFILE='xml-v1+align-qwen36+no-tool+bare+one-stage'

run() { # name, extra args...
  local name=$1; shift
  echo "=== $(date +%H:%M:%S) START $name ==="
  "$@" --output "runs/workbank/$name"
  local rc=$?
  echo "=== $(date +%H:%M:%S) DONE $name rc=$rc ==="
}

declare -A MOD=( [v0]='' [v1]='+merge-users' [v2]='+merge-users-no-nudge' [v3]='+merge-users-rewrite' )

for v in v0 v1 v2 v3; do
  run "closeout-$v-g1k" $CLI agent-eval \
    --completion rwkv-lightning-cuda --api-url "$RWKV_URL" --model "$MODEL" \
    --cases bench/workbank/cases --tool-catalog work-v1 --file-tools lines \
    --profile "${BASE_PROFILE}${MOD[$v]}" \
    --temperature 1 --max-steps 10 --case-parallelism 40 --case-timeout 30m
done

for v in v0 v1 v2 v3; do
  run "closeout-bfcl-$v-g1k" $CLI agent-eval \
    --completion rwkv-lightning-cuda --api-url "$RWKV_URL" --model "$MODEL" \
    --suite bfcl-product \
    --profile "${BASE_PROFILE}${MOD[$v]}" \
    --temperature 1 --case-parallelism 40 --case-timeout 30m
done

for v in v0 v1 v2 v3; do
  run "closeout-boundary-$v-g1k" $CLI agent-eval \
    --completion rwkv-lightning-cuda --api-url "$RWKV_URL" --model "$MODEL" \
    --suite boundary \
    --profile "${BASE_PROFILE}${MOD[$v]}" \
    --temperature 1 --case-parallelism 40 --case-timeout 30m
done

echo "=== $(date +%H:%M:%S) MATRIX COMPLETE ==="
