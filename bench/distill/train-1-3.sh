#!/usr/bin/env bash
# v1.3 masked state tuning: segments.jsonl (train 2051 rows), GPU0/GPU1 LR pair.
#
#   ./train-1-3.sh              start both runs in the background
#   SMOKE=1 ./train-1-3.sh      one optimizer step per GPU, foreground, then exit
#   MODEL=xxx.pth ./train-1-3.sh
#
# Run it from the rwkv_lighting_cuda directory (rwkv_state_tune, vocab and
# segments.jsonl live there). The state only works with the weights it was
# trained on: train on the same .pth the inference endpoint serves.
set -euo pipefail
cd "$(dirname "$0")"

MODEL=${MODEL:-rwkv7-g1k-7.2b-20260930-ctx25600.pth}
DATA=${DATA:-segments.jsonl}
DATA_SHA256=31554122905045712c84574a282356bba5f68046565c724382f58819c01db83d
VOCAB=${VOCAB:-rwkv_vocab_v20230424.txt}
OUT=${OUT:-train-1-3}
SMOKE=${SMOKE:-0}

# 2051 rows / batch 8 = 257 updates per epoch; 3 epochs ~ 771 updates.
# A checkpoint every 86 updates is one per 1/3 epoch (v1.3 plan §6).
# ctx 8192 is required: the longest row is 6925 tokens and the trainer silently
# truncates past --ctx, dropping the final answer of long rows.
COMMON=(--model "$MODEL" --data "$DATA" --vocab "$VOCAB"
  --ctx 8192 --chunk 1024 --wkv_tape
  --batch-size 8 --epochs 3 --warmup-steps 10 --save-every 86 --seed 1234)

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

# name gpu lr lr-final. GPU0 keeps the t927/v1.2 recipe (peak 2e-2, final at
# 1/6 of peak); GPU1 halves it, because the loss now averages over trained
# tokens only (7% of positions) and the old LR is untested on masked loss.
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
