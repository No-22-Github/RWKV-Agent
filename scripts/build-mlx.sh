#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "build-mlx.sh is deprecated; forwarding to build-macos.sh." >&2
exec "$repo_root/scripts/build-macos.sh" "$@"
