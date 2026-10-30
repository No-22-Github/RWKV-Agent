#!/usr/bin/env bash
# v2.3 adapter training: segments-2-3.jsonl (train 5878 rows, ctx 16K pack),
# r16 lr 2e-5, 2 epochs, on the G1L preview rwkv-g1l-7b-temp-3797. NoRA goes
# first (arm C), the MiSS run on the same data (arm B) after it; see
# bench/distill/v2.3/distill-allocation-v2.3.md §6 and §8.
# Built for the Alic-Li Arch server (/mnt/nvme0n1/no22, PRO 6000 96 GB).
#
#   GPUS="0" SMOKE=1 ./train-2-3.sh   one optimizer step on the 8 longest
#                                     rows, foreground: checks memory at
#                                     ctx 16384 and shows the step time
#   GPUS="0" ./train-2-3.sh           start the NoRA run (nohup)
#   ONLY="g1l-miss-r16-lr2e-5-e2" GPUS="0" ./train-2-3.sh
#                                     the MiSS run instead
#   ONLY="g1l-nora-r16-lr2e-5-e2 g1l-miss-r16-lr2e-5-e2" GPUS="0 1" ...
#                                     both at once on two cards
#   MICRO_BSZ=4 ...                   half the packed rows (2048) if the
#                                     smoke run runs out of memory
#   CHUNK=1024 ...                    twice the rows (8192, ~65 GB est.) once
#                                     the default has run and nvidia-smi
#                                     shows the headroom
#   MICRO_BSZ=1 ...                   the v2.2 layout (no packing, chunk
#                                     512), for a binary older than cedc073
#
# GPUS has no default: check nvidia-smi for a free card first.
#
# Run it from /mnt/nvme0n1/no22/rwkv_lighting_cuda, with binaries built from
# Alic-Li/rwkv_lightning_cuda PR #18 (feat/wkv-checkpoint-recompute): NoRA
# (8ee9081), packed micro-batches (cedc073, --micro-bsz) and the 16-row WKV
# checkpoint tape (13-25% faster SFT, bit-identical results). Upload
# local/runs/distill/v2.3/v2.3-pack-20261030/dataset/train/segments-shuffled.jsonl
# as segments-2-3.jsonl: shuffled, ctx 16K pack.
#
# Why these settings: they are the v2.1/v2.2 MiSS settings (v2.1 lr sweep:
# 1e-5 291.5, 2e-5 296.5, 3e-5 280.5), so C vs B compares the method only.
# NoRA requires alpha = rank.
#
# Speed: --micro-bsz 8 runs the whole batch of 8 in one pass, rows packed
# back to back without padding (results equal to one at a time up to FP32
# summation order); each lane walks its sample chunk by chunk.
#
# Memory: every layer keeps its own activation tape for micro-bsz * chunk
# rows (about 21 BF16 vectors of width 4096 per row per layer, so ~5.5 MB a
# row over 32 layers), on top of ~15 GB of weights. The v2.2 runs ended on
# chunk 512 with one lane. 8 x 4096 = 32768 rows would need ~180 GB and ran
# out of memory; 8 x 512 keeps v2.2's per-lane chunk with 8 lanes side by
# side: 4096 rows, ~23 GB of tape, ~40 GB in all (an estimate, not
# measured). Chunk size only costs per-step overhead (the PR #18 benchmarks
# use 256), so more lanes at a small chunk is the better trade.
# The binary also rejects micro-bsz * chunk > 65535. The smoke run (8
# longest rows) is the worst case.
#
# A finished run (adapter-final.pth present) is skipped, so rerunning the
# script after an interruption only starts what is missing.
set -euo pipefail
trap 'echo "train-2-3.sh: line $LINENO failed (exit $?): $BASH_COMMAND" >&2' ERR
cd "$(dirname "$0")"

MODEL=${MODEL:-../rwkv-g1l-7b-temp-3797.pth}
# HF LFS oid of BlinkDL/temp-latest-training-models rwkv-g1l-7b-temp-3797.pth
MODEL_SHA256_PREFIX=7bbef36528bb15e9
DATA=${DATA:-segments-2-3.jsonl}
DATA_SHA256=f1abc80e74ac447e085e8c409293ad3619537fb1188eb4411eb7de2d308c346d
VOCAB=${VOCAB:-rwkv_vocab_v20230424.txt}
OUT=${OUT:-train-2-3}
BASE_OUT=$OUT
CHUNK=${CHUNK:-512}
MICRO_BSZ=${MICRO_BSZ:-8}
SMOKE=${SMOKE:-0}
ONLY=${ONLY:-g1l-nora-r16-lr2e-5-e2}
if [[ -z ${GPUS:-} ]]; then
  echo 'set GPUS, e.g. GPUS="0" (check nvidia-smi for the free cards)' >&2
  exit 1
fi
read -r -a GPU_LIST <<<"$GPUS"
if (( MICRO_BSZ * (CHUNK < 16384 ? CHUNK : 16384) > 65535 )); then
  echo "MICRO_BSZ * CHUNK = $((MICRO_BSZ * CHUNK)) > 65535; the binary rejects it" >&2
  exit 1
fi

# 5878 rows / batch 8 = 735 updates per epoch. A checkpoint every 184
# updates is about one per 1/4 epoch.
COMMON=(--model "$MODEL" --vocab "$VOCAB"
  --targets all --ctx 16384 --chunk "$CHUNK" --wkv_tape
  --batch-size 8 --micro-bsz "$MICRO_BSZ" --warmup-steps 10 --save-every 184)

# name method rank alpha lr lr-final epochs; lr-final is always lr/10
RUNS=(
  "g1l-nora-r16-lr2e-5-e2  nora 16 16 0.00002 0.000002 2"
  "g1l-miss-r16-lr2e-5-e2  miss 16 16 0.00002 0.000002 2"
)
picked=()
for run in "${RUNS[@]}"; do
  read -r name _ <<<"$run"
  if [[ " $ONLY " == *" $name "* ]]; then picked+=("$run"); fi
done
if (( ${#picked[@]} == 0 )); then
  echo "ONLY=\"$ONLY\" matches no run" >&2
  exit 1
fi
RUNS=("${picked[@]}")
if (( ${#GPU_LIST[@]} < ${#RUNS[@]} )); then
  echo "${#RUNS[@]} runs need ${#RUNS[@]} GPUs, GPUS has ${#GPU_LIST[@]}" >&2
  exit 1
fi

for run in "${RUNS[@]}"; do
  read -r _ method _ <<<"$run"
  [[ -e ./rwkv_${method}_tune ]] || { echo "missing: ./rwkv_${method}_tune" >&2; exit 1; }
done
for f in "$MODEL" "$DATA" "$VOCAB"; do
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
  local gpu=$1 data=$2 name=$3 method=$4 rank=$5 alpha=$6 lr=$7 lr_final=$8 epochs=$9 extra=("${@:10}")
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
  local cmd=("./rwkv_${method}_tune" "${COMMON[@]}" --data "$data" --output "$dir"
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
    read -r name method rank alpha lr lr_final epochs <<<"$run"
    run_one "${GPU_LIST[$i]}" "$smoke_data" "$name" "$method" "$rank" "$alpha" "$lr" "$lr_final" 1 --max-steps 1 &
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
    echo "smoke failed; on out of memory retry with MICRO_BSZ=4" >&2
    exit 1
  fi
  echo "smoke ok; start the real runs with the same GPUS (and CHUNK/MICRO_BSZ)"
  exit 0
fi

mkdir -p "$OUT/logs"
if [[ -n ${RUN_CHILD:-} ]]; then
  read -r gpu run <<<"$RUN_CHILD"
  read -r name method rank alpha lr lr_final epochs <<<"$run"
  run_one "$gpu" "$DATA" "$name" "$method" "$rank" "$alpha" "$lr" "$lr_final" "$epochs"
  exit $?
fi
for i in "${!RUNS[@]}"; do
  read -r name _ <<<"${RUNS[$i]}"
  RUN_CHILD="${GPU_LIST[$i]} ${RUNS[$i]}" nohup "$0" >"$OUT/logs/$name.nohup.log" 2>&1 &
  echo "$name: GPU${GPU_LIST[$i]} pid $! -> $OUT/logs/$name.log"
done
echo "follow: tail -f $OUT/logs/*.log"
