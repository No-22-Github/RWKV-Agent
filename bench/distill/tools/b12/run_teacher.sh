#!/usr/bin/env bash
# Runs the S2 contamination faces and the k=3 teacher for one b12 batch, then labels the runs.
#   bench/distill/tools/b12/run_teacher.sh b12c '*-90[7-9]?' [skip-id ...]
# Credentials are proxy-injected in the cloud environment (API_KEY is only a placeholder).
set -euo pipefail
batch="${1:?batch}"; glob="${2:?id glob}"; shift 2
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"; cd "$repo"
T="local/runs/distill/v141/$batch"
rm -rf "$T/cases"; mkdir -p "$T/cases"
for d in bench/distill/v1.41/cases/*/$glob; do
  n="$(basename "$d")"; skip=0
  for s in "$@"; do [ "$s" = "$n" ] && skip=1; done
  [ $skip = 1 ] && continue
  mkdir -p "$T/cases/$(basename "$(dirname "$d")")"; cp -R "$d" "$T/cases/$(basename "$(dirname "$d")")/"
done
echo "cases: $(find "$T/cases" -name case.json | wc -l)"
for t in bench/workbank/cases bench/workbank/cases-shelved bench/holdout/p13 bench/distill/v1/cases-shelved bench/bashprobe/cases; do
  printf '%s ' "$t"; local/bin/rwkv-lab corpus decontam --test "$t" --candidates "$T/cases" 2>&1 | grep -E "files|names" | tr '\n' ' '; echo
done
export API_KEY="${API_KEY:-proxy-injected}"
for k in 0 1 2; do
  local/bin/rwkv-cli agent-eval --completion chat-completions --api-url https://next-token.cc/v1 --model deepseek-flash \
    --api-key-env API_KEY --temperature 0.3 --top-p 1 --tool-catalog agent-tool-v2.0 --file-tools lines --max-steps 16 \
    --max-tokens 4096 --decision-max-tokens 8192 --case-parallelism 8 --case-timeout 30m --remote-batch-wait 0s \
    --chat-system-suffix bench/distill/v1.41/teacher/b12-suffix.txt --cases "$T/cases" --include-draft \
    --output "$T/teacher-k$k" > "$T/k$k.log" 2>&1 || true &
done
wait
grep -h "cases passed" "$T"/k?.log
python3 bench/distill/tools/b12/behavior.py "$T/teacher-k0" "$T/teacher-k1" "$T/teacher-k2" --report "$T/behavior.tsv" | tail -12
