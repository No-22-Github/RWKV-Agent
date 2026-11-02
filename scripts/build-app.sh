#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./scripts/build-app.sh [--with-metal] [--skip-tests]

Build the macOS desktop app and headless server. The default build talks to
remote endpoints only and needs just Go, Node.js and Bun.

Options:
  --with-metal    Add local Metal inference. Requires Apple Silicon, Xcode with
                  the Metal toolchain, CMake, Ninja and the rwkv-mobile submodule.
  --skip-tests    Accepted for compatibility; builds already skip tests.
  -h, --help      Show this help.
EOF
}

with_metal=0
while (( $# > 0 )); do
  case "$1" in
    --with-metal) with_metal=1 ;;
    --skip-tests) ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
frontend_dir="$repo_root/cmd/rwkv-app/frontend"
dist_dir="$repo_root/local/dist"
app_bundle="$dist_dir/RWKV Agent.app"
app_macos="$app_bundle/Contents/MacOS"
app_resources="$app_bundle/Contents/Resources"
export MACOSX_DEPLOYMENT_TARGET=15.0
export CGO_CFLAGS="${CGO_CFLAGS:-} -mmacosx-version-min=15.0"
export CGO_CXXFLAGS="${CGO_CXXFLAGS:-} -mmacosx-version-min=15.0"
export CGO_LDFLAGS="${CGO_LDFLAGS:-} -mmacosx-version-min=15.0"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "RWKV Agent desktop builds currently require macOS." >&2
  exit 1
fi
if (( with_metal )) && [[ "$(uname -m)" != "arm64" ]]; then
  echo "--with-metal requires Apple Silicon." >&2
  exit 1
fi
for command in go bun; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Required build tool is missing: $command" >&2
    exit 1
  fi
done

native_pid=""
if (( with_metal )); then
  echo "[1/4] Preparing the native RWKV runtime..."
  # Fail before downloading frontend tools, including on a fresh checkout.
  if [[ ! -f "$repo_root/third_party/rwkv-mobile/CMakeLists.txt" ]]; then
    git -C "$repo_root" submodule update --init --recursive
  fi
  "$repo_root/scripts/build-macos.sh" --check
else
  echo "[1/4] Skipping local Metal inference (add it with --with-metal)."
fi

source "$repo_root/scripts/lib/frontend-toolchain.sh"

# Native products and frontend assets are independent. Join before Go embeds
# the frontend and links the runtime; also reap the worker on frontend failure.
if (( with_metal )); then
  "$repo_root/scripts/build-macos.sh" &
  native_pid=$!
  trap 'wait "$native_pid" 2>/dev/null || true' EXIT
fi
echo "[2/4] Installing and building the React frontend..."
"$pnpm_command" --dir "$frontend_dir" install --frozen-lockfile
"$pnpm_command" --dir "$frontend_dir" run build
if (( with_metal )); then
  wait "$native_pid"
  trap - EXIT
fi

echo "[3/4] Building the desktop app, headless server and bash sidecar..."
go_tags="production"
if (( with_metal )); then
  go_tags="$go_tags mlx"
fi
mkdir -p "$dist_dir"
# The bash tool's sidecar (native/justbash) is a Bun single-file binary; it
# sits beside the executables, where tools.ResolveBashSidecar looks first.
# The three outputs are independent, so build them side by side and fail if
# any one does.
build_pids=()
(
  cd "$repo_root"
  CGO_ENABLED=1 go build \
    -tags "$go_tags" \
    -trimpath \
    -o "$dist_dir/rwkv-app" \
    ./cmd/rwkv-app
) &
build_pids+=($!)
(
  cd "$repo_root"
  CGO_ENABLED=1 go build \
    -tags "server $go_tags" \
    -trimpath \
    -o "$dist_dir/rwkv-app-server" \
    ./cmd/rwkv-app
) &
build_pids+=($!)
"$repo_root/scripts/build-justbash.sh" "$dist_dir/justbash-sidecar" >/dev/null &
build_pids+=($!)
build_failed=0
for pid in "${build_pids[@]}"; do
  wait "$pid" || build_failed=1
done
if (( build_failed )); then
  echo "A parallel build step failed; see its output above." >&2
  exit 1
fi

if (( with_metal )); then
  for executable in "$dist_dir/rwkv-app" "$dist_dir/rwkv-app-server"; do
    if ! otool -l "$executable" | grep -A2 LC_RPATH | grep -q '@executable_path'; then
      install_name_tool -add_rpath @executable_path "$executable"
    fi
  done
fi

echo "[4/4] Packaging the macOS application bundle..."
rm -rf "$app_bundle"
mkdir -p "$app_macos" "$app_resources"
cp "$repo_root/cmd/rwkv-app/build/darwin/Info.plist" "$app_bundle/Contents/Info.plist"
cp "$repo_root/cmd/rwkv-app/build/darwin/icons.icns" "$app_resources/icons.icns"
cp "$dist_dir/rwkv-app" "$app_macos/RWKV Agent"
if (( with_metal )); then
  cp "$dist_dir/librwkv_agent_runtime.dylib" "$app_macos/librwkv_agent_runtime.dylib"
  cp -R "$dist_dir/mlx-swift_Cmlx.bundle" "$app_resources/mlx-swift_Cmlx.bundle"
fi
if [[ -f "$dist_dir/justbash-sidecar" ]]; then
  cp "$dist_dir/justbash-sidecar" "$app_macos/justbash-sidecar"
fi

echo "Built desktop app: $app_bundle"
echo "Built browser server: $dist_dir/rwkv-app-server --port 8080"
