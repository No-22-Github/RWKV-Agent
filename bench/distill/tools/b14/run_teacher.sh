#!/usr/bin/env bash
# Runs the S2 contamination faces and the k=3 teacher for one b14 batch (an id range), then labels the runs.
#   bench/distill/tools/b14/run_teacher.sh b14a 10001 10040 [skip-id ...]
# Same teacher settings as tools/b12/run_teacher.sh (deepseek-flash, T=0.3, top_p=1, k=3, work-v2, b12 suffix).
# Needs local/bin/rwkv-lab, local/bin/rwkv-cli and the teacher credential (API_KEY, or the proxy in the cloud).
# RWKV_CLI overrides the cli (an API teacher needs a -tags chatcompletions build).
set -euo pipefail
batch="${1:?batch}"; lo="${2:?first id number}"; hi="${3:?last id number}"; shift 3
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"; cd "$repo"
T="local/runs/distill/v142/$batch"
rm -rf "$T/cases"; mkdir -p "$T/cases"
for d in bench/distill/v1.42/cases/*/*-*; do
  n="$(basename "$d")"; num="${n##*-}"
  [ "$num" -ge "$lo" ] && [ "$num" -le "$hi" ] || continue
  skip=0
  for s in "$@"; do [ "$s" = "$n" ] && skip=1; done
  [ $skip = 1 ] && continue
  mkdir -p "$T/cases/$(basename "$(dirname "$d")")"; cp -R "$d" "$T/cases/$(basename "$(dirname "$d")")/"
done
echo "cases: $(find "$T/cases" -name case.json | wc -l)"
for t in bench/workbank/cases bench/workbank/cases-shelved bench/holdout/p13 bench/distill/v1/cases-shelved bench/bashprobe/cases bench/weatherprobe/cases; do
  printf '%s ' "$t"; local/bin/rwkv-lab corpus decontam --test "$t" --candidates "$T/cases" 2>&1 | grep -E "flagged" | tr '\n' ' '; echo
done
export API_KEY="${API_KEY:-proxy-injected}"
for k in 0 1 2; do
  "${RWKV_CLI:-local/bin/rwkv-cli}" agent-eval --completion chat-completions --api-url https://next-token.cc/v1 --model deepseek-flash \
    --api-key-env API_KEY --temperature 0.3 --top-p 1 --tool-catalog work-v2 --file-tools lines --max-steps 16 \
    --max-tokens 4096 --decision-max-tokens 8192 --case-parallelism 8 --case-timeout 30m --remote-batch-wait 0s \
    --chat-system-suffix bench/distill/v1.41/teacher/b12-suffix.txt --cases "$T/cases" --include-draft \
    --output "$T/teacher-k$k" > "$T/k$k.log" 2>&1 || true &
done
wait
grep -h "cases passed" "$T"/k?.log
python3 bench/distill/tools/b14/behavior.py "$T/teacher-k0" "$T/teacher-k1" "$T/teacher-k2" --report "$T/behavior.tsv" | tail -16
