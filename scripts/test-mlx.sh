#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "test-mlx.sh is deprecated; running the macOS native and real-model suites." >&2
"$repo_root/scripts/test-macos-native.sh"
"$repo_root/scripts/test-macos-real-model.sh"
