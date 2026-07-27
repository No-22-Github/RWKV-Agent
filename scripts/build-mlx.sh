#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="$repo_root/third_party/rwkv-mobile"
native_build_dir="$repo_root/build/native/rwkv-mobile"
dist_dir="$repo_root/dist"
resource_dir="$dist_dir/mlx-swift_Cmlx.bundle/Contents/Resources"
asset_dir="$dist_dir/assets"

if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then
  echo "MLX builds currently require macOS on Apple Silicon." >&2
  exit 1
fi
if [[ ! -f "$source_dir/CMakeLists.txt" ]]; then
  echo "rwkv-mobile is missing; run: git submodule update --init --recursive" >&2
  exit 1
fi

cmake -S "$source_dir" -B "$native_build_dir" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_EXAMPLES=OFF \
  -DBUILD_STATIC_LIB=OFF \
  -DENABLE_MLX_BACKEND=ON \
  -DENABLE_NCNN_BACKEND=OFF \
  -DENABLE_WEBRWKV_BACKEND=OFF \
  -DENABLE_LLAMACPP_BACKEND=OFF \
  -DENABLE_QNN_BACKEND=OFF \
  -DENABLE_MNN_BACKEND=OFF \
  -DENABLE_MTK_NP7_BACKEND=OFF \
  -DENABLE_MTK_NP9_BACKEND=OFF \
  -DENABLE_COREML_BACKEND=OFF \
  -DENABLE_VISION=OFF \
  -DENABLE_WHISPER=OFF \
  -DENABLE_TTS=OFF \
  -DENABLE_SERVER=OFF

cmake --build "$native_build_dir" --target rwkv_mobile -j

mkdir -p "$dist_dir" "$resource_dir" "$asset_dir"
cp "$native_build_dir/librwkv_mobile.dylib" "$dist_dir/librwkv_mobile.dylib"
cp "$source_dir/src/backends/mlx/prebuilt/macos-arm64/default.metallib" "$resource_dir/default.metallib"
cp "$source_dir/assets/rwkv_vocab_v20230424.txt" "$asset_dir/rwkv_vocab_v20230424.txt"

(
  cd "$repo_root"
  CGO_ENABLED=1 go build -tags "mlx converter" -trimpath -o "$dist_dir/rwkv-cli" ./cmd/rwkv-cli
)
install_name_tool -add_rpath @executable_path "$dist_dir/rwkv-cli"

echo "Built native MLX CLI: $dist_dir/rwkv-cli"
