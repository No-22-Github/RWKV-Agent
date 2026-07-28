#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="$repo_root/third_party/rwkv-mobile"
output_dir="${1:-$repo_root/build/native/pth-loader}"
patch_path="$repo_root/native/patches/rwkv-mobile-pth-direct.patch"

mkdir -p "$output_dir"
cp "$source_dir/src/pth_loader.h" "$output_dir/pth_loader.h"
cp "$source_dir/src/pth_loader.cpp" "$output_dir/pth_loader.cpp"
cp "$source_dir/src/half.hpp" "$output_dir/half.hpp"
/usr/bin/patch -s -d "$output_dir" -p2 <"$patch_path"
