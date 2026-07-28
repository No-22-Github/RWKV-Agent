#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="$repo_root/third_party/rwkv-mobile"
runtime_source_dir="$repo_root/native/rwkv_agent_runtime"
runtime_build_dir="$repo_root/build/native/agent-runtime"
dist_dir="$repo_root/dist"
resource_dir="$dist_dir/mlx-swift_Cmlx.bundle/Contents/Resources"
asset_dir="$dist_dir/assets"
deployment_target="15.0"

if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then
  echo "The macOS MLX distribution requires Apple Silicon." >&2
  exit 1
fi

for command in cmake ninja go xcrun otool vtool install_name_tool shasum; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Required build tool is missing: $command" >&2
    exit 1
  fi
done

if [[ ! -f "$source_dir/CMakeLists.txt" ]]; then
  echo "rwkv-mobile is missing; run: git submodule update --init --recursive" >&2
  exit 1
fi

export MACOSX_DEPLOYMENT_TARGET="$deployment_target"

cmake -S "$runtime_source_dir" -B "$runtime_build_dir" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_OSX_ARCHITECTURES=arm64 \
  -DCMAKE_OSX_DEPLOYMENT_TARGET="$deployment_target"
cmake --build "$runtime_build_dir" --target rwkv_agent_runtime -j

mkdir -p "$dist_dir" "$resource_dir" "$asset_dir"
cp "$runtime_build_dir/librwkv_agent_runtime.dylib" "$dist_dir/librwkv_agent_runtime.dylib"
cp "$source_dir/src/backends/mlx/prebuilt/macos-arm64/default.metallib" "$resource_dir/default.metallib"
cp "$source_dir/assets/rwkv_vocab_v20230424.txt" "$asset_dir/rwkv_vocab_v20230424.txt"

(
  cd "$repo_root"
  CGO_ENABLED=1 go build \
    -tags "mlx converter" \
    -trimpath \
    -ldflags "-s -w" \
    -o "$dist_dir/rwkv-cli" \
    ./cmd/rwkv-cli
)

if ! otool -l "$dist_dir/rwkv-cli" | grep -A2 LC_RPATH | grep -q '@executable_path'; then
  install_name_tool -add_rpath @executable_path "$dist_dir/rwkv-cli"
fi

install_name_tool -id @rpath/librwkv_agent_runtime.dylib "$dist_dir/librwkv_agent_runtime.dylib"

otool -L "$dist_dir/rwkv-cli" | grep -q '@rpath/librwkv_agent_runtime.dylib'
otool -L "$dist_dir/librwkv_agent_runtime.dylib" >/dev/null
vtool -show-build "$dist_dir/rwkv-cli" | grep -q 'minos 15.0'
vtool -show-build "$dist_dir/librwkv_agent_runtime.dylib" | grep -q 'minos 15.0'
"$dist_dir/rwkv-cli" run --help >/dev/null

commit="$(git -C "$repo_root" rev-parse HEAD)"
if [[ -n "$(git -C "$repo_root" status --porcelain --untracked-files=no)" ]]; then
  commit="${commit}-dirty"
fi
go_version="$(go version | awk '{print $3}')"
cli_sha="$(shasum -a 256 "$dist_dir/rwkv-cli" | awk '{print $1}')"
runtime_sha="$(shasum -a 256 "$dist_dir/librwkv_agent_runtime.dylib" | awk '{print $1}')"
tokenizer_sha="$(shasum -a 256 "$asset_dir/rwkv_vocab_v20230424.txt" | awk '{print $1}')"
metallib_sha="$(shasum -a 256 "$resource_dir/default.metallib" | awk '{print $1}')"

printf '%s\n' \
  '{' \
  '  "schema_version": 1,' \
  "  \"commit\": \"$commit\"," \
  '  "runtime_abi_version": 1,' \
  "  \"go_version\": \"$go_version\"," \
  "  \"deployment_target\": \"$deployment_target\"," \
  '  "sha256": {' \
  "    \"rwkv-cli\": \"$cli_sha\"," \
  "    \"librwkv_agent_runtime.dylib\": \"$runtime_sha\"," \
  "    \"rwkv_vocab_v20230424.txt\": \"$tokenizer_sha\"," \
  "    \"default.metallib\": \"$metallib_sha\"" \
  '  }' \
  '}' >"$dist_dir/build-manifest.json"

echo "Built macOS distribution: $dist_dir/rwkv-cli"
