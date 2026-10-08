#!/usr/bin/env bash
set -euo pipefail

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

if ! command -v node >/dev/null 2>&1; then
  echo "Missing frontend build tool: node" >&2
  echo "Install Node.js 26 (including npm) before building the desktop app." >&2
  exit 1
fi

node_major="$(node -p 'process.versions.node.split(".")[0]')"
if [[ "$node_major" != "26" ]]; then
  echo "RWKV Agent desktop builds require Node.js 26.x; found $(node --version)." >&2
  exit 1
fi

pnpm_version="$(node -p '
  const manifest = require(process.argv[1]);
  const match = /^pnpm@(\d+\.\d+\.\d+)$/.exec(manifest.packageManager || "");
  if (!match) {
    console.error("Expected an exact pnpm version in frontend packageManager.");
    process.exit(1);
  }
  match[1];
' "$frontend_dir/package.json")"

echo "[1/5] Preparing the native RWKV runtime..."
"$repo_root/scripts/build-macos.sh" --with-chat-completions

if command -v pnpm >/dev/null 2>&1 &&
  [[ "$(pnpm --version 2>/dev/null || true)" == "$pnpm_version" ]]; then
  pnpm_command="$(command -v pnpm)"
else
  # Keep the pinned tool in ignored build storage; do not change global pnpm.
  toolchain_dir="$repo_root/local/build/toolchain/pnpm-$pnpm_version"
  pnpm_command="$toolchain_dir/node_modules/.bin/pnpm"
  if [[ ! -x "$pnpm_command" ]] ||
    [[ "$("$pnpm_command" --version 2>/dev/null || true)" != "$pnpm_version" ]]; then
    if ! command -v npm >/dev/null 2>&1; then
      echo "Need npm to prepare pnpm $pnpm_version locally." >&2
      echo "Install Node.js 26 with npm, or put pnpm $pnpm_version on PATH." >&2
      exit 1
    fi
    echo "Preparing project-local pnpm $pnpm_version..."
    npm install --prefix "$toolchain_dir" --no-save --package-lock=false \
      --no-audit --no-fund "pnpm@$pnpm_version"
  fi
fi

if [[ "$("$pnpm_command" --version)" != "$pnpm_version" ]]; then
  echo "Could not prepare the required pnpm $pnpm_version." >&2
  exit 1
fi
echo "Using pnpm $pnpm_version: $pnpm_command"

echo "[2/5] Installing and verifying the React frontend..."
"$pnpm_command" --dir "$frontend_dir" install --frozen-lockfile
"$pnpm_command" --dir "$frontend_dir" test
"$pnpm_command" --dir "$frontend_dir" run build

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
cp "$repo_root/cmd/rwkv-app/build/darwin/icons.icns" "$app_resources/icons.icns"
cp "$dist_dir/rwkv-app" "$app_macos/RWKV Agent"
cp "$dist_dir/librwkv_agent_runtime.dylib" "$app_macos/librwkv_agent_runtime.dylib"
cp -R "$dist_dir/mlx-swift_Cmlx.bundle" "$app_resources/mlx-swift_Cmlx.bundle"
cp -R "$dist_dir/assets" "$app_macos/assets"

echo "Built desktop app: $app_bundle"
echo "Built browser server: $dist_dir/rwkv-app-server --port 8080"
