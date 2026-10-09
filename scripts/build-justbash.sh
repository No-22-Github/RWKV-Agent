#!/usr/bin/env bash
# Builds the single-file just-bash sidecar used by the `bash` tool:
# local/bin/justbash-sidecar (Bun-compiled, no Python / sqlite3).
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="$repo_root/native/justbash"
output="${1:-$repo_root/local/bin/justbash-sidecar}"

if ! command -v bun >/dev/null 2>&1; then
  echo "Required sidecar build tool is missing: bun" >&2
  exit 1
fi

(cd "$source_dir" && bun install --frozen-lockfile --ignore-scripts)
mkdir -p "$(dirname "$output")"
output="$(cd "$(dirname "$output")" && pwd)/$(basename "$output")"
# bun leaves .bun-build scratch files in the cwd; keep them out of the repo root.
(cd "$(dirname "$output")" && bun build --compile --minify "$source_dir/sidecar.ts" --outfile "$output" && rm -f .*.bun-build)
echo "$output"
