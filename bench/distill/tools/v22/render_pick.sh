#!/usr/bin/env bash
# v2.2: one batch drawn from several teacher samples (separate run_teacher.sh
# batches over the same cases), e.g. b22c injection cases on Qwen3.8-27B
# (2026-10-20). Each sample contributes its passing paths only; samples are
# taken in the order given, and per case the first path that passes the filter
# — every step has reasoning, no step over 900 chars, plus filter.py's usual
# checks — is kept and rendered like render.sh.
#
#   bench/distill/tools/v22/render_pick.sh <out-batch> <sample-batch>...
#   bench/distill/tools/v22/render_pick.sh b22c-q38 b22c-q38-27b b22c-q38-27b-s2 b22c-q38-27b-s3
#
# Output under local/runs/distill/v22/<out-batch>/: cases/ (copied from the first
# sample; materialize draws the same tool directory per case id), paths.jsonl,
# script.jsonl, filter-report.json, corpus/.
set -euo pipefail
out="${1:?out batch}"; shift
[ "$#" -ge 1 ] || { echo "need at least one sample batch" >&2; exit 2; }
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"; cd "$repo"
R=local/runs/distill/v22; T="$R/$out"
[ -e "$T" ] && { echo "$T already exists" >&2; exit 2; }
mkdir -p "$T"
cp -R "$R/$1/cases" "$T/cases"
for b in "$@"; do
  diff -rq "$R/$1/cases" "$R/$b/cases" >/dev/null || { echo "$b: cases differ from $1" >&2; exit 2; }
  local/bin/rwkv-lab-v3 corpus paths --run "$R/$b/teacher-k0" --max-per-case 1 --keep-recovery \
    --out "$T/paths-$b.jsonl" --report "$T/paths-report-$b.jsonl"
  cat "$T/paths-$b.jsonl" >> "$T/paths.jsonl"
done
python3 bench/distill/tools/v22/filter.py --script "$T/paths.jsonl" --cases "$T/cases" \
  --out "$T/script.jsonl" --report "$T/filter-report.json" \
  --require-reasoning --max-step-reasoning 900 --one-per-case
local/bin/rwkv-lab-v3 corpus render --cases "$T/cases" --script "$T/script.jsonl" --out "$T/corpus" \
  --source "distill-$out" --profile g1k-think --tool-catalog agent-tool-v3.1 --cli local/bin/rwkv-cli-v3 -- --harness app
