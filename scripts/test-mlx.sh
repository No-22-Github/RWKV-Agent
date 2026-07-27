#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
test_binary="$repo_root/dist/mlx-integration.test"

if [[ -z "${RWKV_TEST_MODEL:-}" || -z "${RWKV_TEST_TOKENIZER:-}" ]]; then
  echo "Set RWKV_TEST_MODEL and RWKV_TEST_TOKENIZER to absolute paths." >&2
  exit 1
fi
if [[ ! -f "$repo_root/build/native/rwkv-mobile/librwkv_mobile.dylib" ]]; then
  echo "Native MLX runtime is missing; run ./scripts/build-mlx.sh first." >&2
  exit 1
fi

(
  cd "$repo_root"
  CGO_ENABLED=1 go test -c -tags mlx -o "$test_binary" ./internal/native/mlx
)
if ! otool -l "$test_binary" | grep -Fq "path @executable_path "; then
  install_name_tool -add_rpath @executable_path "$test_binary"
fi

"$test_binary" -test.run TestNativeMLXGeneration -test.v
