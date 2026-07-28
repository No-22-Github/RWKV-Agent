#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
model_path="${RWKV_TEST_MODEL:-}"
pth_path="${RWKV_TEST_PTH:-}"
tokenizer_path="${RWKV_TEST_TOKENIZER:-$repo_root/dist/assets/rwkv_vocab_v20230424.txt}"
work_dir="${RWKV_TEST_WORK_DIR:-$repo_root/build/real-model-test}"
session_path="$work_dir/replay-$$.rwkv-session"

if [[ -z "$model_path" && -z "$pth_path" ]]; then
  echo "Set RWKV_TEST_MODEL to an MLX model directory or RWKV_TEST_PTH to an RWKV-7 checkpoint." >&2
  exit 2
fi

mkdir -p "$work_dir"
if [[ -z "$model_path" ]]; then
  model_path="$work_dir/model-mlx"
  if [[ ! -f "$model_path/model.safetensors" ]]; then
    "$repo_root/dist/rwkv-cli" convert \
      --input "$pth_path" \
      --output "$model_path" \
      --tokenizer "$tokenizer_path"
  fi
fi

export RWKV_TEST_MODEL="$model_path"
export RWKV_TEST_TOKENIZER="$tokenizer_path"
export DYLD_LIBRARY_PATH="$repo_root/build/native/agent-runtime${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"

(
  cd "$repo_root"
  CGO_ENABLED=1 go test -c -tags mlx \
    -o "$repo_root/dist/rwkvmobile-integration.test" \
    ./internal/inference/backend/rwkvmobile \
)
if ! otool -l "$repo_root/dist/rwkvmobile-integration.test" |
  grep -A2 LC_RPATH |
  grep -q '@executable_path'; then
  install_name_tool -add_rpath @executable_path "$repo_root/dist/rwkvmobile-integration.test"
fi
"$repo_root/dist/rwkvmobile-integration.test" \
  -test.run 'Test(RWKVMobileBackendContract|FourSessionContinuousBatchAndIndependentCancel)' \
  -test.v

"$repo_root/dist/rwkv-cli" run \
  --model "$model_path" \
  --tokenizer "$tokenizer_path" \
  --prompt "请只回答：RWKV native smoke test passed" \
  --max-tokens 32 \
  --reasoning=false

"$repo_root/dist/rwkv-cli" concurrent \
  --model "$model_path" \
  --tokenizer "$tokenizer_path" \
  --concurrency 4 \
  --max-tokens 24 \
  --reasoning=false

printf '%s\n' \
  "我的代号是蓝鲸。" \
  "请记住上一句话。" \
  "/save $session_path" \
  "/exit" |
  "$repo_root/dist/rwkv-cli" run \
    --model "$model_path" \
    --tokenizer "$tokenizer_path" \
    --session "$session_path" \
    --max-tokens 32 \
    --reasoning=false

rm -f "$session_path/revisions/"*/state.bin

printf '%s\n' \
  "我的代号是什么？" \
  "/exit" |
  "$repo_root/dist/rwkv-cli" run \
    --model "$model_path" \
    --tokenizer "$tokenizer_path" \
    --session "$session_path" \
    --max-tokens 32 \
    --reasoning=false
