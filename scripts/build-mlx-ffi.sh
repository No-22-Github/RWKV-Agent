#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
upstream_repo="https://github.com/MollySophia/mlx-swift-examples.git"
upstream_commit="34b276b9c774a8d6465e009382dae12f4e97b849"
source_dir="$repo_root/build/mlx-swift-source"
derived_dir="$repo_root/build/mlx-ffi-derived"
output_dir="$repo_root/build/native/mlx-ffi"
patch_path="$repo_root/native/mlx_model_ffi/direct-pth.patch"
library_path="$output_dir/libMLXModelFFI.a"
metallib_path="$output_dir/default.metallib"

for command in git xcodebuild nm; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Required MLX FFI build tool is missing: $command" >&2
    exit 1
  fi
done

if [[ ! -d "$source_dir/.git" ]]; then
  git clone --filter=blob:none "$upstream_repo" "$source_dir"
  git -C "$source_dir" checkout --detach "$upstream_commit"
fi

actual_commit="$(git -C "$source_dir" rev-parse HEAD)"
if [[ "$actual_commit" != "$upstream_commit" ]]; then
  echo "Unexpected MLXModelFFI source revision: $actual_commit" >&2
  echo "Expected: $upstream_commit" >&2
  exit 1
fi

ffi_source="$source_dir/Tools/MLXModelFFI/MLXModelFFI.swift"
if ! grep -Fq '@_cdecl("mlx_model_load_pth")' "$ffi_source"; then
  git -C "$source_dir" apply --check "$patch_path"
  git -C "$source_dir" apply "$patch_path"
fi

xcodebuild \
  -project "$source_dir/mlx-swift-examples.xcodeproj" \
  -scheme MLXModelFFI \
  -configuration Release \
  -destination "platform=macOS,arch=arm64" \
  -derivedDataPath "$derived_dir" \
  build \
  CODE_SIGNING_ALLOWED=NO

product_dir="$derived_dir/Build/Products/Release"
mkdir -p "$output_dir"
cp "$product_dir/libMLXModelFFI.a" "$library_path"
cp \
  "$product_dir/mlx-swift_Cmlx.bundle/Contents/Resources/default.metallib" \
  "$metallib_path"

if ! nm -gU "$library_path" 2>/dev/null |
  awk '$NF == "_mlx_model_load_pth" { found = 1 } END { exit !found }'; then
  echo "Built MLXModelFFI is missing direct PTH ABI" >&2
  exit 1
fi

echo "Built direct-PTH MLXModelFFI: $library_path"
