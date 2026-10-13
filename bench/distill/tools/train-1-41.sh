#!/usr/bin/env bash
# v1.41 masked state tuning: segments-1-41.jsonl (train 3662 rows), GPU0/GPU1 LR pair.
# Same recipe as train-1-3.sh; only the data and the step counts change.
#
#   ./train-1-41.sh              start both runs in the background
#   SMOKE=1 ./train-1-41.sh      one optimizer step per GPU, foreground, then exit
#   MODEL=xxx.pth ./train-1-41.sh
#
# Run it from the rwkv_lighting_cuda directory (rwkv_state_tune, vocab and
# segments-1-41.jsonl live there). Upload
# local/runs/distill/v141/final-20261013/dataset/train/segments-1-41.jsonl: the
# packed segments.jsonl shuffled with random.Random(20261013), because
# rwkv_state_tune reads rows in file order every epoch (--seed does not shuffle)
# and the packed file has all b12 rows at the end. The name keeps the v1.3
# segments.jsonl intact. The state only works with the weights it was trained
# on: train on the same .pth the inference endpoint serves.
set -euo pipefail
cd "$(dirname "$0")"

MODEL=${MODEL:-rwkv7-g1k-7.2b-20260930-ctx25600.pth}
DATA=${DATA:-segments-1-41.jsonl}
DATA_SHA256=feb2fd6b4ea874c298e1822ea62ec79305ca7711c0618b3dbe77859dc62d6a75
VOCAB=${VOCAB:-rwkv_vocab_v20230424.txt}
OUT=${OUT:-train-1-41}
SMOKE=${SMOKE:-0}

# 3662 rows / batch 8 = 458 updates per epoch (trainer rounds up); 3 epochs = 1374 updates.
# A checkpoint every 153 updates is one per 1/3 epoch, as in v1.3.
# ctx 8192: the longest row is 8124 tokens and the trainer silently truncates
# past --ctx, dropping the final answer of long rows.
COMMON=(--model "$MODEL" --data "$DATA" --vocab "$VOCAB"
  --ctx 8192 --chunk 1024 --wkv_tape
  --batch-size 8 --epochs 3 --warmup-steps 10 --save-every 153 --seed 1234)

for f in ./rwkv_state_tune "$MODEL" "$DATA" "$VOCAB"; do
  [[ -e $f ]] || { echo "missing: $f" >&2; exit 1; }
done
actual=$(sha256sum "$DATA" | cut -d' ' -f1)
if [[ $actual != "$DATA_SHA256" ]]; then
  echo "$DATA sha256 $actual, want $DATA_SHA256" >&2
  exit 1
fi

if [[ $SMOKE == 1 ]]; then
  OUT=$OUT-smoke
  COMMON+=(--max-steps 1)
fi

# name gpu lr lr-final, the v1.3 pair: GPU0 peak 2e-2, GPU1 peak 1e-2,
# both decaying to 1/6 of peak.
RUNS=(
  "lr2e-2 0 0.02 0.0033333333"
  "lr1e-2 1 0.01 0.0016666667"
)

pids=()
for run in "${RUNS[@]}"; do
  read -r name gpu lr lr_final <<<"$run"
  dir=$OUT/$name
  if [[ -d $dir && -n $(ls -A "$dir") ]]; then
    echo "$dir is not empty; move it away first" >&2
    exit 1
  fi
  mkdir -p "$dir"
  cmd=(./rwkv_state_tune "${COMMON[@]}" --output "$dir" --lr "$lr" --lr-final "$lr_final")
  {
    echo "date: $(date -Is)"
    echo "gpu: $gpu"
    echo "model: $MODEL ($(stat -c %s "$MODEL") bytes)"
    echo "data: $DATA sha256 $DATA_SHA256"
    echo "cmd: CUDA_VISIBLE_DEVICES=$gpu ${cmd[*]}"
  } >"$dir/run.txt"
  CUDA_VISIBLE_DEVICES=$gpu nohup "${cmd[@]}" >"$dir/train.log" 2>&1 &
  pids+=($!)
  echo "$name: GPU$gpu pid $! -> $dir/train.log"
done

if [[ $SMOKE == 1 ]]; then
  status=0
  for pid in "${pids[@]}"; do wait "$pid" || status=1; done
  for run in "${RUNS[@]}"; do
    read -r name _ <<<"$run"
    echo "== $name"
    tail -n 5 "$OUT/$name/train.log"
  done
  exit $status
fi

echo "follow: tail -f $OUT/*/train.log"
