#!/usr/bin/env bash
# v2.0 MiSS (thinking) adapter training: segments-2-0.jsonl (train 2142 rows),
# an 8-run sweep scheduled on 4 GPUs: each GPU works through its own lane of
# runs one after another, the four lanes run in parallel.
#
#   ./train-2-0.sh              start the four lanes in the background (nohup)
#   SMOKE=1 ./train-2-0.sh      one optimizer step of every run on the first
#                               GPU, foreground (checks each rank fits)
#   ONLY="r16-lr1e-4-e2 r64-lr1e-4-e2" ./train-2-0.sh   only these runs
#   GPUS="0 1 2 3" MODEL=xxx.pth ./train-2-0.sh
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
read -r -a GPU_LIST <<<"${GPUS:-0 1 2 3}"
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

# lane name rank alpha lr lr-final epochs
# Base point: rank 16, lr 1e-4 (the MiSS README example), 2 epochs; the
# 1/4-epoch checkpoints include the end of epoch 1. Two one-knob axes around
# it (lr x4, rank x4) and one long run. lr-final is always lr/10.
# Lanes are balanced in optimizer updates: a 2-epoch run is 536, the 4-epoch
# run 1072, so lane 0 holds 1608 and the others 1072.
RUNS=(
  "0 r16-lr1e-4-e4   16  16 0.0001 0.00001  4"
  "0 r256-lr1e-4-e2 256 256 0.0001 0.00001  2"
  "1 r16-lr1e-4-e2   16  16 0.0001 0.00001  2"
  "1 r16-lr3e-5-e2   16  16 0.00003 0.000003 2"
  "2 r16-lr3e-4-e2   16  16 0.0003 0.00003  2"
  "2 r16-lr1e-3-e2   16  16 0.001  0.0001   2"
  "3 r4-lr1e-4-e2     4   4 0.0001 0.00001  2"
  "3 r64-lr1e-4-e2   64  64 0.0001 0.00001  2"
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
  local gpu=$1 name=$2 rank=$3 alpha=$4 lr=$5 lr_final=$6 epochs=$7 extra=("${@:8}")
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
    echo "gpu: $gpu"
    echo "model: $MODEL ($(stat -c %s "$MODEL") bytes)"
    echo "data: $DATA sha256 $DATA_SHA256"
    echo "cmd: CUDA_VISIBLE_DEVICES=$gpu ${cmd[*]}"
  } >"$log.run.txt"
  echo "$name: start on GPU$gpu $(date -Is) -> $log.log"
  CUDA_VISIBLE_DEVICES=$gpu "${cmd[@]}" >"$log.log" 2>&1
  echo "$name: exit $? $(date -Is)"
}

if [[ $SMOKE == 1 ]]; then
  OUT=$OUT-smoke
  rm -rf "$OUT"
  for run in "${RUNS[@]}"; do
    read -r _ name rank alpha lr lr_final epochs <<<"$run"
    run_one "${GPU_LIST[0]}" "$name" "$rank" "$alpha" "$lr" "$lr_final" "$epochs" --max-steps 1 || true
    tail -n 3 "$OUT/logs/$name.log"
  done
  exit 0
fi

lane() {
  local lane=$1 gpu=${GPU_LIST[$1]}
  for run in "${RUNS[@]}"; do
    read -r l name rank alpha lr lr_final epochs <<<"$run"
    [[ $l == "$lane" ]] || continue
    if [[ -n $ONLY && " $ONLY " != *" $name "* ]]; then continue; fi
    # one failed run does not stop the lane; its log says why
    run_one "$gpu" "$name" "$rank" "$alpha" "$lr" "$lr_final" "$epochs" || true
  done
  echo "lane $lane (GPU$gpu) finished $(date -Is)"
}

mkdir -p "$OUT/logs"
if [[ -n ${LANE_CHILD:-} ]]; then
  lane "$LANE_CHILD"
  exit 0
fi
for i in "${!GPU_LIST[@]}"; do
  LANE_CHILD=$i nohup "$0" >"$OUT/logs/lane$i.log" 2>&1 &
  echo "lane $i: GPU${GPU_LIST[$i]} pid $! -> $OUT/logs/lane$i.log"
done
echo "follow: tail -f $OUT/logs/lane*.log"
