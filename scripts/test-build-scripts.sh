#!/usr/bin/env bash
set -euo pipefail

# Exercise dependency failures and pnpm selection without compiling native code.
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
test_root="$(mktemp -d "${TMPDIR:-/tmp}/rwkv-build-test.XXXXXX")"
trap 'rm -rf "$test_root"' EXIT
mock_bin="$test_root/bin"
fixture="$test_root/repo with spaces"
mkdir -p "$mock_bin" "$fixture/scripts" "$fixture/third_party/rwkv-mobile" \
  "$fixture/cmd/rwkv-app/frontend" "$fixture/cmd/rwkv-app/build/darwin"
cp "$repo_root/scripts/build-macos.sh" "$repo_root/scripts/build-app.sh" "$fixture/scripts/"
cp "$repo_root/cmd/rwkv-app/build/darwin/Info.plist" "$repo_root/cmd/rwkv-app/build/darwin/icons.icns" "$fixture/cmd/rwkv-app/build/darwin/"
touch "$fixture/third_party/rwkv-mobile/CMakeLists.txt"
echo '{"packageManager":"pnpm@11.7.0"}' >"$fixture/cmd/rwkv-app/frontend/package.json"
ln -s "$(command -v node)" "$mock_bin/node"
export MOCK_BIN="$mock_bin" MOCK_REPO="$fixture" MOCK_LOG="$test_root/commands.log"
export MOCK_PNPM_VERSION=10.33.2
: >"$MOCK_LOG"

cat >"$mock_bin/driver" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
case "${0##*/}" in
  uname) if [[ "$1" == -s ]]; then echo Darwin; else echo arm64; fi ;;
  xcrun)
    # Finding the launcher still succeeds when the compiler cannot execute.
    if [[ "$*" == *metal* && "$*" == *--version* ]]; then
      exit "${MOCK_METAL_FAILURE:-0}"
    fi
    exit "${MOCK_SDK_FAILURE:-0}"
    ;;
  pnpm)
    if [[ "${1:-}" == --version ]]; then echo "$MOCK_PNPM_VERSION"; else
      printf 'pnpm %s %s\n' "$MOCK_PNPM_VERSION" "$*" >>"$MOCK_LOG"
    fi
    ;;
  npm)
    printf 'npm %s\n' "$*" >>"$MOCK_LOG"
    prefix=""; version=""
    while (( $# )); do
      case "$1" in
        --prefix) prefix="$2"; shift ;;
        pnpm@*) version="${1#pnpm@}" ;;
      esac
      shift
    done
    mkdir -p "$prefix/node_modules/.bin"
    printf '#!/usr/bin/env bash\nexport MOCK_PNPM_VERSION=%q\nexec "$MOCK_BIN/pnpm" "$@"\n' "$version" \
      >"$prefix/node_modules/.bin/pnpm"
    chmod +x "$prefix/node_modules/.bin/pnpm"
    ;;
  go)
    while (( $# )); do
      if [[ "$1" == -o ]]; then touch "$2"; chmod +x "$2"; break; fi
      shift
    done
    ;;
  otool) printf 'LC_RPATH\npath @executable_path\n' ;;
esac
EOF
chmod +x "$mock_bin/driver"
for command in uname xcrun pnpm npm cmake ninja go git xcodebuild swift otool vtool install_name_tool shasum nm; do
  ln -s driver "$mock_bin/$command"
done
export PATH="$mock_bin:$PATH"

expect_failure() {
  local message="$1"
  shift
  if "$@" >"$test_root/output.log" 2>&1; then
    echo "Expected failure: $message" >&2
    exit 1
  fi
  if [[ -n "$message" ]] && ! grep -Fq "$message" "$test_root/output.log"; then
    cat "$test_root/output.log" >&2
    exit 1
  fi
}

expect_failure 'xcodebuild -downloadComponent MetalToolchain' \
  env MOCK_METAL_FAILURE=1 bash "$fixture/scripts/build-macos.sh" --check
expect_failure 'does not provide the macOS SDK' \
  env MOCK_SDK_FAILURE=1 bash "$fixture/scripts/build-macos.sh" --check
bash "$fixture/scripts/build-macos.sh" --check >"$test_root/output.log"
grep -Fq 'macOS build environment is ready.' "$test_root/output.log"
echo 'PASS: SDK and executable Metal checks'

# Desktop tests stub only native compilation; pnpm selection uses the real script.
cat >"$fixture/scripts/build-macos.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
if [[ "${MOCK_METAL_FAILURE:-0}" != 0 ]]; then exit 1; fi
if [[ "${1:-}" == --check ]]; then
  test -f "$MOCK_REPO/third_party/rwkv-mobile/CMakeLists.txt"
  exit
fi
# A normal native build initializes missing submodule sources automatically.
touch "$MOCK_REPO/third_party/rwkv-mobile/CMakeLists.txt"
dist="$MOCK_REPO/local/dist"
mkdir -p "$dist/mlx-swift_Cmlx.bundle/Contents/Resources" "$dist/assets"
touch "$dist/librwkv_agent_runtime.dylib" \
  "$dist/mlx-swift_Cmlx.bundle/Contents/Resources/default.metallib" \
  "$dist/assets/rwkv_vocab_v20230424.txt"
EOF

expect_failure '' env MOCK_METAL_FAILURE=1 bash "$fixture/scripts/build-app.sh"
test ! -s "$MOCK_LOG" # Native dependency checks must precede tool downloads.
rm "$fixture/third_party/rwkv-mobile/CMakeLists.txt"
bash "$fixture/scripts/build-app.sh" >"$test_root/output.log"
test -f "$fixture/third_party/rwkv-mobile/CMakeLists.txt"
grep -Fq 'pnpm@11.7.0' "$MOCK_LOG"
test "$(grep -c '^pnpm 11.7.0 ' "$MOCK_LOG")" -eq 3
test -f "$fixture/local/dist/RWKV Agent.app/Contents/MacOS/RWKV Agent"
: >"$MOCK_LOG"
bash "$fixture/scripts/build-app.sh" >"$test_root/output.log"
test "$(grep -c '^npm ' "$MOCK_LOG" || true)" -eq 0
test "$(grep -c '^pnpm 11.7.0 ' "$MOCK_LOG")" -eq 3
echo 'PASS: native source initialization, pinned pnpm bootstrap and cache reuse'

: >"$MOCK_LOG"
MOCK_PNPM_VERSION=11.7.0 bash "$fixture/scripts/build-app.sh" >"$test_root/output.log"
test "$(grep -c '^npm ' "$MOCK_LOG" || true)" -eq 0
grep -Fq "Using pnpm 11.7.0: $mock_bin/pnpm" "$test_root/output.log"
echo 'PASS: matching pnpm on PATH is used directly'

echo '{"packageManager":"pnpm@11.8.0"}' >"$fixture/cmd/rwkv-app/frontend/package.json"
: >"$MOCK_LOG"
bash "$fixture/scripts/build-app.sh" >"$test_root/output.log"
grep -Fq 'pnpm@11.8.0' "$MOCK_LOG"
test "$(grep -c '^pnpm 11.8.0 ' "$MOCK_LOG")" -eq 3
echo 'PASS: changing the manifest pin selects the new pnpm version'
