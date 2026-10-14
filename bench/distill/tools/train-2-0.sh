#!/usr/bin/env bash
# v2.0 MiSS (thinking) adapter training: segments-2-0.jsonl (train 2142 rows),
# one GPU, runs queued one after another (a small parameter sweep).
#
#   ./train-2-0.sh              start the queue in the background (nohup)
#   SMOKE=1 ./train-2-0.sh      one optimizer step of the first run, foreground
#   ONLY=r16-lr1e-4 ./train-2-0.sh   run just the named entries (space separated)
#   GPU=3 MODEL=xxx.pth ./train-2-0.sh
#
# Run it from the rwkv_lighting_cuda directory (rwkv_miss_tune, vocab, model
# and segments-2-0.jsonl live there). Upload
# local/runs/distill/v20/final-20261014b/dataset/train/segments-shuffled.jsonl
# as segments-2-0.jsonl: the trainer reads rows in file order and the packed
# file keeps one trajectory's step rows together; this copy is shuffled with
# random.Random(20261014).
#
# rwkv_miss_tune must be built from Alic-Li/rwkv_lightning_cuda main (or any
# tree containing 47df608): the v1.8.0 release has MiSS but not the segments
# loss mask, and would train on the whole prompt.
#
# A finished run (adapter-final.pth present) is skipped, so rerunning the
# script after an interruption continues the queue from the next run.
set -euo pipefail
cd "$(dirname "$0")"

MODEL=${MODEL:-rwkv7-g1k-7.2b-20260930-ctx25600.pth}
DATA=${DATA:-segments-2-0.jsonl}
DATA_SHA256=afbf2fc552a743981a7384233c3d6a83ac719dbcac3ab63a876974071421356d
VOCAB=${VOCAB:-rwkv_vocab_v20230424.txt}
OUT=${OUT:-train-2-0}
GPU=${GPU:-3}
SMOKE=${SMOKE:-0}
ONLY=${ONLY:-}

# 2142 rows / batch 8 = 268 updates per epoch. A checkpoint every 67 updates
# is one per 1/4 epoch.
# ctx 8192: the longest row is 8077 tokens (finalize drops rows over 8128);
# the README example's ctx 4096 would silently cut the trained step off the
# long rows, because the trained segment is always the last one.
COMMON=(--model "$MODEL" --data "$DATA" --vocab "$VOCAB"
  --targets all --ctx 8192 --chunk 1024 --wkv_tape
  --batch-size 8 --warmup-steps 10 --save-every 67)

# name rank alpha lr lr-final epochs
# First entry = the MiSS README production example (rank 16, alpha 16,
# lr 1e-4 -> 1e-5, 1 epoch), only ctx changed. The rest move one knob each.
RUNS=(
  "r16-lr1e-4-e1  16 16 0.0001 0.00001 1"
  "r16-lr3e-4-e1  16 16 0.0003 0.00003 1"
  "r16-lr1e-4-e2  16 16 0.0001 0.00001 2"
  "r64-lr1e-4-e1  64 64 0.0001 0.00001 1"
)

for f in ./rwkv_miss_tune "$MODEL" "$DATA" "$VOCAB"; do
  [[ -e $f ]] || { echo "missing: $f" >&2; exit 1; }
done
actual=$(sha256sum "$DATA" | cut -d' ' -f1)
if [[ $actual != "$DATA_SHA256" ]]; then
  echo "$DATA sha256 $actual, want $DATA_SHA256" >&2
  exit 1
fi

run_one() {
  local name=$1 rank=$2 alpha=$3 lr=$4 lr_final=$5 epochs=$6 extra=("${@:7}")
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
  local cmd=(./rwkv_miss_tune "${COMMON[@]}" --output "$dir" --rank "$rank" --alpha "$alpha"
    --lr "$lr" --lr-final "$lr_final" --epochs "$epochs" "${extra[@]}")
  {
    echo "date: $(date -Is)"
    echo "gpu: $GPU"
    echo "model: $MODEL ($(stat -c %s "$MODEL") bytes)"
    echo "data: $DATA sha256 $DATA_SHA256"
    echo "cmd: CUDA_VISIBLE_DEVICES=$GPU ${cmd[*]}"
  } >"$log.run.txt"
  echo "$name: start $(date -Is) -> $log.log"
  CUDA_VISIBLE_DEVICES=$GPU "${cmd[@]}" >"$log.log" 2>&1
  echo "$name: exit $? $(date -Is)"
}

if [[ $SMOKE == 1 ]]; then
  OUT=$OUT-smoke
  read -r name rank alpha lr lr_final epochs <<<"${RUNS[0]}"
  rm -rf "$OUT"
  run_one "$name" "$rank" "$alpha" "$lr" "$lr_final" "$epochs" --max-steps 1 || true
  tail -n 15 "$OUT/logs/$name.log"
  exit 0
fi

queue() {
  for run in "${RUNS[@]}"; do
    read -r name rank alpha lr lr_final epochs <<<"$run"
    if [[ -n $ONLY && " $ONLY " != *" $name "* ]]; then continue; fi
    # one failed run does not stop the queue; its log says why
    run_one "$name" "$rank" "$alpha" "$lr" "$lr_final" "$epochs" || true
  done
  echo "queue finished $(date -Is)"
}

mkdir -p "$OUT/logs"
if [[ ${QUEUE_CHILD:-0} == 1 ]]; then
  queue
  exit 0
fi
QUEUE_CHILD=1 nohup "$0" >"$OUT/logs/queue.log" 2>&1 &
echo "queue pid $! on GPU$GPU -> $OUT/logs/queue.log"
echo "follow: tail -f $OUT/logs/queue.log $OUT/logs/*.log"
