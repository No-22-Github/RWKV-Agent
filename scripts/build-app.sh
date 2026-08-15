#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
frontend_dir="$repo_root/cmd/rwkv-app/frontend"
dist_dir="$repo_root/dist"
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
"$repo_root/scripts/build-macos.sh" --with-chat-completions

echo "[2/5] Installing and verifying the React frontend..."
pnpm --dir "$frontend_dir" install --frozen-lockfile
pnpm --dir "$frontend_dir" test
pnpm --dir "$frontend_dir" run build

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

echo "[5/5] Packaging the macOS application bundle..."
rm -rf "$app_bundle"
mkdir -p "$app_macos" "$app_resources"
cp "$repo_root/cmd/rwkv-app/build/darwin/Info.plist" "$app_bundle/Contents/Info.plist"
cp "$dist_dir/rwkv-app" "$app_macos/RWKV Agent"
cp "$dist_dir/librwkv_agent_runtime.dylib" "$app_macos/librwkv_agent_runtime.dylib"
cp -R "$dist_dir/mlx-swift_Cmlx.bundle" "$app_resources/mlx-swift_Cmlx.bundle"
cp -R "$dist_dir/assets" "$app_macos/assets"

echo "Built desktop app: $app_bundle"
echo "Built browser server: $dist_dir/rwkv-app-server --port 8080"
