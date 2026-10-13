#!/usr/bin/env bash
# Upload the train-1-41 checkpoints and bench them on both bank catalogs.
#
#   bench/distill/tools/test-1-41.sh <train-1-41 dir> [state_id ...]
#
# V1 (work-v1): workbank 148 + bfcl-product 60 through `rwkv-lab bench sweep`.
# V2 (work-v2): bench/bashprobe 26 cases (+ bash, get_weather).
# Arms: none, v13b-s688 (v1.3 pick, already on the endpoint), then every
# v1.41 checkpoint: v141a-sNNN (lr2e-2) / v141b-sNNN (lr1e-2), finals first.
#
# Every run uses the 688cbfa1 cli and sidecar: b12 was rendered with them and
# main's 51eef6ff changes the work-v2 bash description. sweep picks the cli up
# from RWKV_CLI; the lab itself is the main build (local/bin/rwkv-lab).
# Reruns resume: sweep skips finished runs, bashprobe skips dirs with summary.json.
set -euo pipefail
cd "$(dirname "$0")/../../.."
SRC=${1:?usage: test-1-41.sh <train-1-41 dir> [state_id ...]}
shift
API=${API:-http://100.64.0.4:8018/v1}
# Uploads go through Cloudflare (same deployment): since 2026-10-13 the direct
# Tailscale link stalls on request bodies over ~1 MB (bulk UDP upstream is
# throttled; small inference requests are fine), and a stalled upload also
# wedges the tunnel for a few seconds. UPLOAD_API=$API restores direct uploads.
UPLOAD_API=${UPLOAD_API:-https://api-7b.rwkvos.com/v1}
MODEL=${MODEL:-rwkv7-g1k-7.2b-20260930-ctx25600}
OUT=${OUT:-local/runs/bench-20261013-v141}
K=${K:-0}  # replica indices, e.g. K="1 2" for the replica pass
STATES=local/states/v141
CLI=local/bin/rwkv-cli-688cbfa1
LAB=local/bin/rwkv-lab
export RWKV_CLI=$PWD/$CLI
export RWKV_JUSTBASH_SIDECAR=$PWD/local/bin/justbash-sidecar-688cbfa1
export NO_PROXY="100.64.0.4" no_proxy="100.64.0.4"
# Cloudflare Access credentials: the environment, else ~/.config/rwkv/cf.env,
# whose keys are the header names (CF-Access-Client-Id=...).
CF_ENV=${CF_ENV:-$HOME/.config/rwkv/cf.env}
cf_value() { sed -nE "s/^[[:space:]]*(export[[:space:]]+)?$1[[:space:]]*=[[:space:]]*\"?([^\"]*)\"?.*/\2/p" "$CF_ENV" | head -n 1; }
if [[ -z ${RWKV_CF_ID:-} && -r $CF_ENV ]]; then
  RWKV_CF_ID=$(cf_value CF-Access-Client-Id) RWKV_CF_SECRET=$(cf_value CF-Access-Client-Secret)
fi
if [[ $UPLOAD_API == https://* && ( -z ${RWKV_CF_ID:-} || -z ${RWKV_CF_SECRET:-} ) ]]; then
  echo "Cloudflare upload needs RWKV_CF_ID/RWKV_CF_SECRET (or $CF_ENV); or set UPLOAD_API=$API" >&2
  exit 1
fi
export RWKV_CF_ID=${RWKV_CF_ID:-unused} RWKV_CF_SECRET=${RWKV_CF_SECRET:-unused}

[[ -x $CLI && -x $LAB ]] || { echo "need $CLI and $LAB (go build -o $LAB ./cmd/rwkv-lab)" >&2; exit 1; }

mkdir -p "$STATES" "$OUT"
for pair in "lr2e-2:v141a" "lr1e-2:v141b"; do
  dir=$SRC/${pair%%:*}
  tag=${pair#*:}
  [[ -d $dir ]] || { echo "missing $dir" >&2; exit 1; }
  for f in "$dir"/state-step-*.pth "$dir"/state-final.pth; do
    [[ -e $f ]] || continue
    base=$(basename "$f" .pth)
    if [[ $base == state-final ]]; then
      name=$tag-fin
    else
      name=$tag-s$((10#${base#state-step-}))
    fi
    [[ -e $STATES/$name.pth ]] || cp "$f" "$STATES/$name.pth"
  done
done
(cd "$STATES" && shasum -a 256 ./*.pth >SHA256SUMS)

# Upload serially (parallel uploads 502), skipping what the endpoint has.
cf=(--api-header-env CF-Access-Client-Id=RWKV_CF_ID --api-header-env CF-Access-Client-Secret=RWKV_CF_SECRET)
have=$($CLI state list --api-url "$API" 2>/dev/null | awk 'NR>1{print $1}')
for f in "$STATES"/*.pth; do
  id=$(basename "$f")
  if grep -qx "$id" <<<"$have"; then continue; fi
  until $CLI state upload --api-url "$UPLOAD_API" "${cf[@]}" --file "$f"; do
    echo "upload $id failed; retry in 60s" >&2
    sleep 60
  done
done
have=$($CLI state list --api-url "$API" 2>/dev/null | awk 'NR>1{print $1}')

if (($# == 0)); then
  ids=(none v13b-s688 v141a-fin v141b-fin)
  for s in 1224 1071 918 765 612 459 306 153; do ids+=(v141a-s$s v141b-s$s); done
else
  ids=("$@")
fi
for id in "${ids[@]}"; do
  id=${id%.pth}
  [[ $id == none ]] && continue
  grep -qx "$id.pth" <<<"$have" || { echo "STOP: $id.pth is not on the endpoint; rerun to upload" >&2; exit 2; }
done

state_args() { [[ $1 == none ]] || echo "--state-id $1.pth"; }

# Per arm and replica: V1 (workbank + bfcl-product, 64 in flight across the
# two suites via sweep), then V2 (bashprobe, all 26 cases in flight), so each
# state is complete before the next starts.
for id in "${ids[@]}"; do
  id=${id%.pth}
  for k in $K; do
    echo "=== $(date +%T) V1 $id k$k"
    # shellcheck disable=SC2046
    $LAB bench sweep --out "$OUT" --arms g1k-agent --suites workbank,bfcl-product --k "$k" \
      --model "$MODEL" --api-url "$API" --prefix "$id" $(state_args "$id") --max-concurrency 64
    run=$OUT/$id-bashprobe-g1k-agent-k$k
    if [[ ! -e $run/summary.json ]]; then
      rm -rf "$run"
      echo "=== $(date +%T) V2 $id k$k"
      # shellcheck disable=SC2046
      $CLI agent-eval --completion rwkv-lightning-cuda --model "$MODEL" --api-url "$API" \
        --profile g1k --strict-spec \
        --cases bench/bashprobe/cases --tool-catalog work-v2 --file-tools lines --include-draft \
        --max-steps 16 --max-tokens 4096 --decision-max-tokens 2048 --case-parallelism 26 --case-timeout 30m \
        --remote-batch-wait 0s --sampling g1k-agent $(state_args "$id") --output "$run" ||
        true # exits 1 whenever a case fails; run check below is the validity gate
      $LAB run check "$run" --arm g1k-agent --rwkv --cases 26
    fi
    echo "=== $(date +%T) ARM-DONE $id k$k"
  done
done
echo "=== $(date +%T) done"
