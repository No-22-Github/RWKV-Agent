#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="$repo_root/third_party/rwkv-mobile"
runtime_source_dir="$repo_root/native/rwkv_agent_runtime"
runtime_build_dir="$repo_root/build/native/agent-runtime"
mlx_ffi_dir="$repo_root/build/native/mlx-ffi"
dist_dir="$repo_root/dist"
resource_dir="$dist_dir/mlx-swift_Cmlx.bundle/Contents/Resources"
asset_dir="$dist_dir/assets"
deployment_target="15.0"

usage() {
  cat <<'EOF'
Usage: ./scripts/build-macos.sh [--check]

Build the Apple Silicon macOS distribution.

Options:
  --check   Verify the local build environment without compiling.
  -h        Show this help.
EOF
}

check_only=0
case "${1:-}" in
  "")
    ;;
  --check)
    check_only=1
    ;;
  -h|--help)
    usage
    exit 0
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then
  echo "This build currently requires an Apple Silicon Mac running macOS 15 or newer." >&2
  exit 1
fi

missing_commands=()
for command in cmake ninja go git xcodebuild swift xcrun otool vtool install_name_tool shasum nm; do
  if ! command -v "$command" >/dev/null 2>&1; then
    missing_commands+=("$command")
  fi
done

if (( ${#missing_commands[@]} > 0 )); then
  echo "Missing build tools: ${missing_commands[*]}" >&2
  echo "Install Xcode, then install the command-line dependencies:" >&2
  echo "  brew install cmake ninja go" >&2
  exit 1
fi

if ! xcrun --sdk macosx --show-sdk-path >/dev/null 2>&1 ||
  ! xcrun --find metal >/dev/null 2>&1; then
  echo "The selected Xcode does not provide the macOS SDK and Metal toolchain." >&2
  echo "Select the full Xcode installation, for example:" >&2
  echo "  sudo xcode-select -s /Applications/Xcode.app/Contents/Developer" >&2
  exit 1
fi

if [[ ! -f "$source_dir/CMakeLists.txt" ]]; then
  if (( check_only )); then
    echo "rwkv-mobile is not initialized." >&2
    echo "Run: git submodule update --init --recursive" >&2
    exit 1
  fi
  echo "Initializing the pinned rwkv-mobile dependency..."
  git -C "$repo_root" submodule update --init --recursive
fi

if [[ ! -f "$source_dir/CMakeLists.txt" ]]; then
  echo "rwkv-mobile is still missing after submodule initialization." >&2
  exit 1
fi

if (( check_only )); then
  echo "macOS build environment is ready."
  exit 0
fi

export MACOSX_DEPLOYMENT_TARGET="$deployment_target"

echo "[1/4] Building the pinned MLX Swift bridge..."
"$repo_root/scripts/build-mlx-ffi.sh"

echo "[2/4] Building the native RWKV runtime..."
cmake -S "$runtime_source_dir" -B "$runtime_build_dir" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_OSX_ARCHITECTURES=arm64 \
  -DCMAKE_OSX_DEPLOYMENT_TARGET="$deployment_target" \
  -DRWKV_AGENT_MLX_LIB="$mlx_ffi_dir/libMLXModelFFI.a"
cmake --build "$runtime_build_dir" --target rwkv_agent_runtime -j

echo "[3/4] Building rwkv-cli..."
mkdir -p "$dist_dir" "$resource_dir" "$asset_dir"
cp "$runtime_build_dir/librwkv_agent_runtime.dylib" "$dist_dir/librwkv_agent_runtime.dylib"
cp "$mlx_ffi_dir/default.metallib" "$resource_dir/default.metallib"
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

echo "[4/4] Verifying and packaging the distribution..."
if ! otool -l "$dist_dir/rwkv-cli" | grep -A2 LC_RPATH | grep -q '@executable_path'; then
  install_name_tool -add_rpath @executable_path "$dist_dir/rwkv-cli"
fi

install_name_tool -id @rpath/librwkv_agent_runtime.dylib "$dist_dir/librwkv_agent_runtime.dylib"

otool -L "$dist_dir/rwkv-cli" | grep -q '@rpath/librwkv_agent_runtime.dylib'
otool -L "$dist_dir/librwkv_agent_runtime.dylib" >/dev/null
vtool -show-build "$dist_dir/rwkv-cli" | grep -q 'minos 15.0'
vtool -show-build "$dist_dir/librwkv_agent_runtime.dylib" | grep -q 'minos 15.0'
"$dist_dir/rwkv-cli" run --help >/dev/null 2>&1

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
  '  "runtime_abi_version": 2,' \
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
