#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="$repo_root/third_party/rwkv-mobile"
output_dir="${1:-$repo_root/local/build/native/pth-loader}"
patch_path="$repo_root/native/patches/rwkv-mobile-pth-direct.patch"

mkdir -p "$output_dir"
# Patch in isolation, then replace only changed files. Reconfiguring CMake must
# not invalidate object files when upstream sources and our patch are unchanged.
prepared_dir="$(mktemp -d "$output_dir/.prepare.XXXXXX")"
trap 'rm -rf "$prepared_dir"' EXIT
for filename in pth_loader.h pth_loader.cpp half.hpp; do
  cp "$source_dir/src/$filename" "$prepared_dir/$filename"
done
/usr/bin/patch -s -d "$prepared_dir" -p2 <"$patch_path"
for filename in pth_loader.h pth_loader.cpp half.hpp; do
  if ! cmp -s "$prepared_dir/$filename" "$output_dir/$filename"; then
    mv "$prepared_dir/$filename" "$output_dir/$filename"
  fi
done
