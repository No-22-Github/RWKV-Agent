#!/usr/bin/env bash
# v2.1 MiSS (thinking) adapter training: segments-2-1.jsonl (train 5512 rows),
# three low-lr runs, one per GPU, all in parallel. Built for rwkv-101
# (rwkv@100.64.0.19, RTX 4090 24 GB).
#
#   GPUS="1 2 3" SMOKE=1 ./train-2-1.sh   one optimizer step of every run on
#                                         the 8 longest rows, one GPU each,
#                                         foreground: checks 24 GB is enough
#   GPUS="1 2 3" ./train-2-1.sh           start the three runs (nohup)
#   CHUNK=512 ...                         lower state-passing chunk if the
#                                         smoke run runs out of memory
#   ONLY="r16-lr2e-5-e2" GPUS="2" ...     only these runs, on these GPUs
#
# GPUS has no default: the card the inference server sits on must not be
# picked by accident. Check nvidia-smi first.
#
# Run it from ~/no22/rwkv_lighting_cuda (rwkv_miss_tune and the vocab live
# there; the model is one level up). Upload
# local/runs/distill/v21/final-20261018/dataset/train/segments-shuffled.jsonl
# as segments-2-1.jsonl: shuffled, ctx 8192 pack (longest row 8121 tokens).
#
# Why only low lr: on v2.0 (2142 rows) lr 3e-4 and 1e-3 broke the model,
# lr 1e-4 and 3e-5 tied (workbank +19/-14, bfcl +0/-5), rank 16 beat 4 and
# 64, and 4 epochs did not beat 2. This pack is 2.6x larger, so each epoch
# already makes 2.6x the updates; 3e-5 is the v2.0 best and the anchor.
#
# rwkv_miss_tune must contain 47df608 (segments loss mask): v1.8.1 and later
# releases do, v1.8.0 does not and would train on the whole prompt.
#
# A finished run (adapter-final.pth present) is skipped, so rerunning the
# script after an interruption only starts what is missing.
set -euo pipefail
cd "$(dirname "$0")"

MODEL=${MODEL:-../rwkv7-g1k-7.2b-20260930-ctx25600.pth}
MODEL_SHA256_PREFIX=0853d4ce
DATA=${DATA:-segments-2-1.jsonl}
DATA_SHA256=2fbf6760482561c3fae2e1e5354bc49d20d81aec480a37ee80c66e46463afe07
VOCAB=${VOCAB:-rwkv_vocab_v20230424.txt}
OUT=${OUT:-train-2-1}
BASE_OUT=$OUT
CHUNK=${CHUNK:-1024}
SMOKE=${SMOKE:-0}
ONLY=${ONLY:-}
if [[ -z ${GPUS:-} ]]; then
  echo 'set GPUS, e.g. GPUS="1 2 3" (check nvidia-smi for the free cards)' >&2
  exit 1
fi
read -r -a GPU_LIST <<<"$GPUS"

# 5512 rows / batch 8 = 689 updates per epoch. A checkpoint every 172
# updates is one per 1/4 epoch, so the end of epoch 1 is among them.
# The batch is accumulated one sample at a time: memory does not grow with
# --batch-size, only with ctx/chunk.
COMMON=(--model "$MODEL" --vocab "$VOCAB"
  --targets all --ctx 8192 --chunk "$CHUNK" --wkv_tape
  --batch-size 8 --warmup-steps 10 --save-every 172)

# name rank alpha lr lr-final epochs; lr-final is always lr/10
RUNS=(
  "r16-lr1e-5-e2  16 16 0.00001 0.000001 2"
  "r16-lr2e-5-e2  16 16 0.00002 0.000002 2"
  "r16-lr3e-5-e2  16 16 0.00003 0.000003 2"
)
if [[ -n $ONLY ]]; then
  picked=()
  for run in "${RUNS[@]}"; do
    read -r name _ <<<"$run"
    if [[ " $ONLY " == *" $name "* ]]; then picked+=("$run"); fi
  done
  RUNS=("${picked[@]}")
fi
if (( ${#GPU_LIST[@]} < ${#RUNS[@]} )); then
  echo "${#RUNS[@]} runs need ${#RUNS[@]} GPUs, GPUS has ${#GPU_LIST[@]}" >&2
  exit 1
fi

for f in ./rwkv_miss_tune "$MODEL" "$DATA" "$VOCAB"; do
  [[ -e $f ]] || { echo "missing: $f" >&2; exit 1; }
done
actual=$(sha256sum "$DATA" | cut -d' ' -f1)
if [[ $actual != "$DATA_SHA256" ]]; then
  echo "$DATA sha256 $actual, want $DATA_SHA256" >&2
  exit 1
fi
# The adapter records the base model fingerprint; a different file of the
# same name would give adapters the inference server refuses.
if [[ ! -e $OUT/.model-ok ]]; then
  echo "checking $MODEL sha256 (about a minute)..."
  model_sha=$(sha256sum "$MODEL" | cut -d' ' -f1)
  if [[ $model_sha != "$MODEL_SHA256_PREFIX"* ]]; then
    echo "$MODEL sha256 $model_sha, want $MODEL_SHA256_PREFIX..." >&2
    exit 1
  fi
  mkdir -p "$OUT"
  echo "$model_sha" >"$OUT/.model-ok"
fi

run_one() {
  local gpu=$1 data=$2 name=$3 rank=$4 alpha=$5 lr=$6 lr_final=$7 epochs=$8 extra=("${@:9}")
  local dir=$OUT/$name log=$OUT/logs/$name
  if [[ -e $dir/adapter-final.pth ]]; then
    echo "$name: done, skipping"
    return 0
  fi
  if [[ -e $dir ]]; then
    echo "$name: $dir exists without adapter-final.pth; move it away first" >&2
    return 1
  fi
  mkdir -p "$OUT/logs"
  local cmd=(./rwkv_miss_tune "${COMMON[@]}" --data "$data" --output "$dir"
    --rank "$rank" --alpha "$alpha" --lr "$lr" --lr-final "$lr_final"
    --epochs "$epochs" "${extra[@]}")
  {
    echo "date: $(date -Is)"
    echo "gpu: $gpu"
    echo "model: $MODEL sha256 $(cat "$OUT/.model-ok" 2>/dev/null || echo '?')"
    echo "data: $data"
    echo "cmd: CUDA_VISIBLE_DEVICES=$gpu ${cmd[*]}"
  } >"$log.run.txt"
  echo "$name: start on GPU$gpu $(date -Is) -> $log.log"
  local status=0
  CUDA_VISIBLE_DEVICES=$gpu "${cmd[@]}" >"$log.log" 2>&1 || status=$?
  echo "$name: exit $status $(date -Is)"
  return "$status"
}

if [[ $SMOKE == 1 ]]; then
  # One step on the longest rows, so the peak memory of the real run shows
  # up here rather than hours in.
  OUT=$OUT-smoke
  rm -rf "$OUT"
  mkdir -p "$OUT/logs"
  cp "$BASE_OUT/.model-ok" "$OUT/"
  smoke_data=$OUT/longest-8.jsonl
  awk '{print length($0) "\t" NR}' "$DATA" | sort -rn | head -n 8 | cut -f2 |
    sort -n | awk 'NR==FNR{want[$1]=1; next} want[FNR]' - "$DATA" >"$smoke_data"
  i=0
  pids=()
  for run in "${RUNS[@]}"; do
    read -r name rank alpha lr lr_final epochs <<<"$run"
    run_one "${GPU_LIST[$i]}" "$smoke_data" "$name" "$rank" "$alpha" "$lr" "$lr_final" 1 --max-steps 1 &
    pids+=($!)
    i=$((i + 1))
  done
  fail=0
  for pid in "${pids[@]}"; do wait "$pid" || fail=1; done
  for run in "${RUNS[@]}"; do
    read -r name _ <<<"$run"
    echo "== $name"
    tail -n 5 "$OUT/logs/$name.log"
  done
  if (( fail )); then
    echo "smoke failed; on out of memory retry with CHUNK=512" >&2
    exit 1
  fi
  echo "smoke ok; start the real runs with the same GPUS"
  exit 0
fi

mkdir -p "$OUT/logs"
if [[ -n ${RUN_CHILD:-} ]]; then
  read -r gpu run <<<"$RUN_CHILD"
  read -r name rank alpha lr lr_final epochs <<<"$run"
  run_one "$gpu" "$DATA" "$name" "$rank" "$alpha" "$lr" "$lr_final" "$epochs"
  exit $?
fi
for i in "${!RUNS[@]}"; do
  read -r name _ <<<"${RUNS[$i]}"
  RUN_CHILD="${GPU_LIST[$i]} ${RUNS[$i]}" nohup "$0" >"$OUT/logs/$name.nohup.log" 2>&1 &
  echo "$name: GPU${GPU_LIST[$i]} pid $! -> $OUT/logs/$name.log"
done
echo "follow: tail -f $OUT/logs/*.log"
