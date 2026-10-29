#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export DYLD_LIBRARY_PATH="$repo_root/local/build/native/agent-runtime${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"

"$repo_root/scripts/build-mlx-ffi.sh"

# The ASan runtime build does not depend on the Go tests, so overlap them.
asan_build_dir="$repo_root/local/build/native/agent-runtime-asan"
(
  cmake -S "$repo_root/native/rwkv_agent_runtime" -B "$asan_build_dir" -G Ninja \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_OSX_ARCHITECTURES=arm64 \
    -DCMAKE_OSX_DEPLOYMENT_TARGET=15.0 \
    -DCMAKE_CXX_FLAGS="-fsanitize=address -fno-omit-frame-pointer" \
    -DCMAKE_SHARED_LINKER_FLAGS="-fsanitize=address"
  cmake --build "$asan_build_dir" --target rwkv_agent_runtime -j
  cmake --build "$asan_build_dir" --target rwkv_agent_runtime_lifecycle_test rwkv7_index_test -j
) &
asan_pid=$!
trap 'wait "$asan_pid" 2>/dev/null || true' EXIT

(
  cd "$repo_root"
  # -race runs the same tests as a plain run, so it replaces it.
  go test -race ./...
  CGO_ENABLED=1 go test -tags mlx ./internal/native/rwkvmobile ./internal/inference/backend/rwkvmobile
)

wait "$asan_pid"
trap - EXIT
ASAN_OPTIONS=detect_leaks=0 ctest --test-dir "$asan_build_dir" --output-on-failure
