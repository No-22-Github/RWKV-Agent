#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./scripts/build-app.sh [--skip-tests]

Build the macOS desktop app and headless server.

Options:
  --skip-tests    Accepted for compatibility; builds already skip tests.
  -h, --help      Show this help.
EOF
}

while (( $# > 0 )); do
  case "$1" in
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

if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then
  echo "RWKV Agent desktop builds currently require Apple Silicon macOS." >&2
  exit 1
fi

echo "[1/5] Preparing the native RWKV runtime..."
# Fail before downloading frontend tools, including on a fresh checkout.
if [[ ! -f "$repo_root/third_party/rwkv-mobile/CMakeLists.txt" ]]; then
  git -C "$repo_root" submodule update --init --recursive
fi
"$repo_root/scripts/build-macos.sh" --check

source "$repo_root/scripts/lib/frontend-toolchain.sh"

# Native products and frontend assets are independent. Join before Go embeds
# the frontend and links the runtime; also reap the worker on frontend failure.
"$repo_root/scripts/build-macos.sh" --with-chat-completions &
native_pid=$!
trap 'wait "$native_pid" 2>/dev/null || true' EXIT
echo "[2/5] Installing and building the React frontend..."
"$pnpm_command" --dir "$frontend_dir" install --frozen-lockfile
"$pnpm_command" --dir "$frontend_dir" run build
wait "$native_pid"
trap - EXIT

echo "[3/5] Building the Wails V3 desktop executable..."
(
  cd "$repo_root"
  CGO_ENABLED=1 go build \
    -tags "production mlx chatcompletions" \
    -trimpath \
    -o "$dist_dir/rwkv-app" \
    ./cmd/rwkv-app
)

echo "[4/5] Building the Wails V3 headless server executable..."
(
  cd "$repo_root"
  CGO_ENABLED=1 go build \
    -tags "production server mlx chatcompletions" \
    -trimpath \
    -o "$dist_dir/rwkv-app-server" \
    ./cmd/rwkv-app
)

for executable in "$dist_dir/rwkv-app" "$dist_dir/rwkv-app-server"; do
  if ! otool -l "$executable" | grep -A2 LC_RPATH | grep -q '@executable_path'; then
    install_name_tool -add_rpath @executable_path "$executable"
  fi
done

# The bash tool's sidecar (native/justbash) is a Bun single-file binary; it
# sits beside the executables, where tools.ResolveBashSidecar looks first.
if command -v bun >/dev/null 2>&1; then
  "$repo_root/scripts/build-justbash.sh" "$dist_dir/justbash-sidecar" >/dev/null
else
  echo "warning: bun not found; the bash tool will be unavailable in this build" >&2
  rm -f "$dist_dir/justbash-sidecar"
fi

echo "[5/5] Packaging the macOS application bundle..."
rm -rf "$app_bundle"
mkdir -p "$app_macos" "$app_resources"
cp "$repo_root/cmd/rwkv-app/build/darwin/Info.plist" "$app_bundle/Contents/Info.plist"
cp "$repo_root/cmd/rwkv-app/build/darwin/icons.icns" "$app_resources/icons.icns"
cp "$dist_dir/rwkv-app" "$app_macos/RWKV Agent"
cp "$dist_dir/librwkv_agent_runtime.dylib" "$app_macos/librwkv_agent_runtime.dylib"
cp -R "$dist_dir/mlx-swift_Cmlx.bundle" "$app_resources/mlx-swift_Cmlx.bundle"
cp -R "$dist_dir/assets" "$app_macos/assets"
if [[ -f "$dist_dir/justbash-sidecar" ]]; then
  cp "$dist_dir/justbash-sidecar" "$app_macos/justbash-sidecar"
fi

echo "Built desktop app: $app_bundle"
echo "Built browser server: $dist_dir/rwkv-app-server --port 8080"
