#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
data_repo="$repo_root/third_party/gorilla"
data_commit="6ea57973c7a6097fd7c5915698c54c17c5b1b6c8"
evaluator_version="2026.3.23"
venv=${BFCL_VENV:-"$repo_root/.venv"}

python_bin=""
use_uv=""
if [ -n "${BFCL_PYTHON:-}" ]; then
  python_bin=$BFCL_PYTHON
elif command -v uv >/dev/null 2>&1; then
  # uv downloads a CPython 3.12 on demand, so this works on machines with no
  # system 3.12. It only builds the venv; the interpreter inside is stock CPython.
  use_uv=1
elif command -v python3.12 >/dev/null 2>&1 && python3.12 -c 'import sys; raise SystemExit(sys.version_info[:2] != (3, 12))' 2>/dev/null; then
  python_bin=$(command -v python3.12)
elif command -v pyenv >/dev/null 2>&1; then
  python_bin="$(pyenv prefix 3.12)/bin/python"
else
  echo "BFCL setup requires Python 3.12; install uv, or set BFCL_PYTHON to a 3.12 executable." >&2
  exit 1
fi

if [ -e "$data_repo/.git" ]; then
  if ! git -C "$data_repo" diff --quiet || ! git -C "$data_repo" diff --cached --quiet; then
    echo "Refusing to update dirty BFCL data checkout: $data_repo" >&2
    exit 1
  fi
  git -C "$data_repo" fetch origin "$data_commit"
else
  git clone --filter=blob:none --no-checkout https://github.com/ShishirPatil/gorilla.git "$data_repo"
  git -C "$data_repo" sparse-checkout init --cone
  git -C "$data_repo" sparse-checkout set berkeley-function-call-leaderboard/bfcl_eval/data
fi

git -C "$data_repo" checkout --detach "$data_commit"

if [ -x "$venv/bin/python" ]; then
  if ! "$venv/bin/python" -c 'import sys; raise SystemExit(sys.version_info[:2] != (3, 12))'; then
    echo "Existing BFCL virtual environment is not Python 3.12: $venv" >&2
    exit 1
  fi
elif [ -n "$use_uv" ]; then
  uv venv --python 3.12 --seed "$venv"
else
  "$python_bin" -m venv "$venv"
fi

if [ -n "$use_uv" ]; then
  # CPU-only torch: everything this harness scores goes through a remote API, so
  # the default CUDA wheels would only add ~4.4 GB of NVIDIA libraries that a
  # GPU-less machine can never use.
  uv pip install --python "$venv/bin/python" --torch-backend cpu \
    "bfcl-eval==$evaluator_version" "soundfile==0.14.0"
else
  "$venv/bin/python" -m pip install --upgrade pip
  "$venv/bin/python" -m pip install \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    "bfcl-eval==$evaluator_version" "soundfile==0.14.0"
fi

actual_commit=$(git -C "$data_repo" rev-parse HEAD)
actual_version=$("$venv/bin/python" -c 'from importlib.metadata import version; print(version("bfcl_eval"))')

test "$actual_commit" = "$data_commit"
test "$actual_version" = "$evaluator_version"

printf 'BFCL data commit: %s\n' "$actual_commit"
printf 'bfcl-eval version: %s\n' "$actual_version"
