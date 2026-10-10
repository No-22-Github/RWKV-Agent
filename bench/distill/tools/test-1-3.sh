#!/usr/bin/env bash
# Upload the train-1-3 checkpoints and bench them (g1k wire, the training format).
#
#   bench/distill/tools/test-1-3.sh <train-1-3 dir> [state_id ...]
#
# <train-1-3 dir> is the trainer output copied from the training machine
# (lr2e-2/ and lr1e-2/ with state-step-XXXXXXXX.pth and state-final.pth).
# Checkpoints are copied to local/states/v13/ under endpoint names
# v13a-sNNN.pth (lr2e-2) and v13b-sNNN.pth (lr1e-2): the endpoint uses the
# uploaded file name as state_id. Without state_id arguments every checkpoint
# is benched, final first, then from the latest step down.
set -euo pipefail
cd "$(dirname "$0")/../../.."
SRC=${1:?usage: test-1-3.sh <train-1-3 dir> [state_id ...]}
shift
API=${API:-http://100.64.0.4:8018/v1}
MODEL=${MODEL:-rwkv7-g1k-7.2b-20260930-ctx25600}
OUT=${OUT:-local/runs/bench-$(date +%Y%m%d)-v13}
STATES=local/states/v13
export NO_PROXY="100.64.0.4" no_proxy="100.64.0.4"
export RWKV_CF_ID=${RWKV_CF_ID:-unused} RWKV_CF_SECRET=${RWKV_CF_SECRET:-unused}

mkdir -p "$STATES"
for pair in "lr2e-2:v13a" "lr1e-2:v13b"; do
  dir=$SRC/${pair%%:*}
  tag=${pair#*:}
  [[ -d $dir ]] || { echo "missing $dir" >&2; exit 1; }
  for f in "$dir"/state-step-*.pth "$dir"/state-final.pth; do
    [[ -e $f ]] || continue
    base=$(basename "$f" .pth)
    if [[ $base == state-final ]]; then
      name=$tag-fin
    else
      name=$(printf '%s-s%03d' "$tag" "$((10#${base#state-step-}))")
    fi
    # macOS cp -n exits 1 when the target exists, which set -e would abort on.
    [[ -e $STATES/$name.pth ]] || cp "$f" "$STATES/$name.pth"
  done
done
(cd "$STATES" && shasum -a 256 ./*.pth >SHA256SUMS && cat SHA256SUMS)

# Upload serially (parallel uploads 502), skipping what the endpoint has.
have=$(./local/bin/rwkv-cli state list --api-url "$API" 2>/dev/null | awk 'NR>1{print $1}')
for f in "$STATES"/*.pth; do
  id=$(basename "$f")
  if grep -qx "$id" <<<"$have"; then
    echo "on endpoint: $id"
    continue
  fi
  until ./local/bin/rwkv-cli state upload --api-url "$API" --file "$f"; do
    echo "upload $id failed; retry in 60s" >&2
    sleep 60
  done
done
have=$(./local/bin/rwkv-cli state list --api-url "$API" 2>/dev/null | awk 'NR>1{print $1}')

if (($# == 0)); then
  # final first, then newest step down: the late checkpoints are the likely picks.
  mapfile -t ids < <(cd "$STATES" && { ls -1 -- *-fin.pth; ls -1 -- *-s*.pth | sort -t- -k2 -r; })
else
  ids=("$@")
fi
for id in "${ids[@]}"; do
  [[ $id == *.pth ]] || id=$id.pth
  if ! grep -qx "$id" <<<"$have"; then
    echo "STOP: $id is not on the endpoint (service restarted?); rerun to upload" >&2
    exit 2
  fi
  echo "=== $(date +%T) $id"
  ./local/bin/rwkv-lab bench sweep --out "$OUT" --arms g1k-agent --suites workbank,bfcl-product --k 0 \
    --model "$MODEL" --api-url "$API" --prefix "${id%.pth}" --state-id "$id" --max-concurrency 64
done
echo "=== $(date +%T) done; score with docs/evaluations/g1k-official-format-20261003/summarize.py $OUT"
