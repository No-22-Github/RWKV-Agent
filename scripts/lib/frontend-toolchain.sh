#!/usr/bin/env bash
# Shared by build-app.sh and test-app.sh; caller sets repo_root/frontend_dir.

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

