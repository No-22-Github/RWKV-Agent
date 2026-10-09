#!/usr/bin/env bash
set -euo pipefail

case "${1:-}" in
  -h|--help)
    echo "Usage: ./scripts/test-app.sh [vitest arguments...]"
    echo "Install pinned frontend dependencies and run frontend tests without building the app."
    exit 0
    ;;
esac

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
frontend_dir="$repo_root/cmd/rwkv-app/frontend"
source "$repo_root/scripts/lib/frontend-toolchain.sh"
"$pnpm_command" --dir "$frontend_dir" install --frozen-lockfile
"$pnpm_command" --dir "$frontend_dir" test "$@"
