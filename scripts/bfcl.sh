#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
venv=${BFCL_VENV:-"$repo_root/.venv"}

if [ ! -x "$venv/bin/python" ]; then
  echo "BFCL environment is missing; run scripts/setup-bfcl.sh first." >&2
  exit 1
fi

exec "$venv/bin/python" "$repo_root/scripts/bfcl.py" "$@"
