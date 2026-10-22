#!/usr/bin/env bash
# v2.2 MiSS (thinking) adapter training: segments-2-2.jsonl (train 5953 rows,
# ctx 16K pack), one run at the v2.1 winner lr 2e-5 (r16, 2 epochs), on the
# G1K release base rwkv7-g1k-7.2b-20260930-ctx25600 (the same base as v2.1).
# The first run on the G1L preview rwkv-g1l-7b-temp-3797 went bad, so its
# output stays in train-2-2/ and this run writes to train-2-2-g1k/.
# Built for the Alic-Li Arch server
# (/mnt/nvme0n1/no22, rwkv_lighting_cuda v1.8.6 release, which ships
# rwkv_miss_tune with the segments loss mask).
#
#   GPUS="0" SMOKE=1 ./train-2-2.sh   one optimizer step on the 8 longest
#                                     rows, foreground: checks memory at
#                                     ctx 16384
#   GPUS="0" ./train-2-2.sh           start the run (nohup)
#   CHUNK=8192 ...                    lower state-passing chunk if the smoke
#                                     run runs out of memory
#
# GPUS has no default: check nvidia-smi for a free card first.
#
# Run it from /mnt/nvme0n1/no22/rwkv_lighting_cuda (rwkv_miss_tune and the
# vocab live there; the model is one level up). Upload
# local/runs/distill/v22/final-20261021/dataset/train/segments-shuffled.jsonl
# as segments-2-2.jsonl: shuffled, ctx 16K pack (longest row 16226 tokens).
#
# Why lr 2e-5: the v2.1 sweep on the new exam gave 1e-5 291.5, 2e-5 296.5,
# 3e-5 280.5 (2e-5 vs v2.0 +95/-54, p=0.001). v2.2 is about the same size
# (5953 vs 5512 rows), so the same lr carries over.
#
# A finished run (adapter-final.pth present) is skipped, so rerunning the
# script after an interruption only starts what is missing.
set -euo pipefail
trap 'echo "train-2-2.sh: line $LINENO failed (exit $?): $BASH_COMMAND" >&2' ERR
cd "$(dirname "$0")"

MODEL=${MODEL:-../rwkv7-g1k-7.2b-20260930-ctx25600.pth}
# Same prefix as train-2-1.sh
MODEL_SHA256_PREFIX=0853d4ce
DATA=${DATA:-segments-2-2.jsonl}
DATA_SHA256=4b119f4d4d97ad0d39c14ebc3a3be248c127b4c8d712bd006c54a3eb0849dcd9
VOCAB=${VOCAB:-rwkv_vocab_v20230424.txt}
OUT=${OUT:-train-2-2-g1k}
BASE_OUT=$OUT
# 16384 = the whole ctx in one chunk; the PRO 6000 (96 GB) has the memory.
CHUNK=${CHUNK:-16384}
SMOKE=${SMOKE:-0}
ONLY=${ONLY:-}
if [[ -z ${GPUS:-} ]]; then
  echo 'set GPUS, e.g. GPUS="1 2 3" (check nvidia-smi for the free cards)' >&2
  exit 1
fi
read -r -a GPU_LIST <<<"$GPUS"

# 5953 rows / batch 8 = 745 updates per epoch. A checkpoint every 186
# updates is about one per 1/4 epoch.
# The batch is accumulated one sample at a time: memory does not grow with
# --batch-size, only with ctx/chunk.
COMMON=(--model "$MODEL" --vocab "$VOCAB"
  --targets all --ctx 16384 --chunk "$CHUNK" --wkv_tape
  --batch-size 8 --warmup-steps 10 --save-every 186)

# name rank alpha lr lr-final epochs; lr-final is always lr/10
RUNS=(
  "g1k-r16-lr2e-5-e2  16 16 0.00002 0.000002 2"
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
  # awk 'NR<=8', not head: head closes the pipe early, sort dies of SIGPIPE
  # and pipefail turns that into a silent exit 141.
  awk '{print length($0) "\t" NR}' "$DATA" | sort -rn | awk 'NR<=8' | cut -f2 |
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
    echo "smoke failed; on out of memory retry with CHUNK=8192" >&2
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
