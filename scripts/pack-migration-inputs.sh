#!/usr/bin/env bash
#
# pack-migration-inputs.sh — 打包 Python→Go 工具迁移所需的**历史产物**。
#
# 背景：docs/go-tooling-migration.md §2.3 的 M0 基线要在**起点 commit 的工作树**里跑
# 20 条旧命令，把输出存成基线，迁移后逐条对比。工具本身在 git 里，但输入（runs/、
# datasets/、state_output/、outputs/）都被 gitignore，只在作者的 macOS 上。这个脚本
# 把输入打成一个包，拷到开发 VPS 后解压到仓库根目录即可。
#
# 在仓库根目录运行：
#   bash scripts/pack-migration-inputs.sh              # standard（默认）
#   bash scripts/pack-migration-inputs.sh --minimal    # 只打 §2.3 点名的那几个 run 目录
#   bash scripts/pack-migration-inputs.sh --full       # runs/ datasets/ state_output/ outputs/ 全量
#   bash scripts/pack-migration-inputs.sh --list       # 只报体积，不打包
#   bash scripts/pack-migration-inputs.sh --zip        # 产出 .zip 而不是 .tar.gz
#   bash scripts/pack-migration-inputs.sh --extra 路径  # 追加一个路径（可重复，例如凭据 JSON）
#
# 产出：
#   migration-inputs-<日期>.tar.gz（或 .zip）
#   migration-inputs-<日期>.manifest.txt   ← 体积清单 + 缺失项，请连这个一起发回来
#   清单也会以 MIGRATION-INPUTS-MANIFEST.txt 的名字打进包内。
#
# 兼容 macOS 自带的 bash 3.2（不用关联数组、不用 mapfile、不用 ${var,,}）。

set -euo pipefail

# ---------------------------------------------------------------- 参数

MODE=standard
KIND=targz
DRY=0
EXTRAS=""
OUT=""

usage() {
    sed -n '3,28p' "$0" | sed 's/^# \{0,1\}//'
    exit "${1:-0}"
}

while [ $# -gt 0 ]; do
    case "$1" in
        --minimal) MODE=minimal ;;
        --standard) MODE=standard ;;
        --full) MODE=full ;;
        --zip) KIND=zip ;;
        --targz|--tgz) KIND=targz ;;
        --list|--dry-run) DRY=1 ;;
        --out) shift; OUT="${1:-}" ;;
        --extra) shift; EXTRAS="$EXTRAS
${1:-}" ;;
        -h|--help) usage 0 ;;
        *) echo "未知参数：$1" >&2; usage 2 ;;
    esac
    shift
done

# ---------------------------------------------------------------- 前置检查

ROOT=$(pwd)
if [ ! -f "$ROOT/go.mod" ] || [ ! -f "$ROOT/docs/go-tooling-migration.md" ]; then
    echo "错误：请在仓库根目录运行（当前 $ROOT）" >&2
    exit 2
fi

HOST=$(hostname 2>/dev/null || echo unknown)
STAMP=$(date +%Y%m%d-%H%M%S)
[ -n "$OUT" ] || OUT="migration-inputs-$STAMP.$([ "$KIND" = zip ] && echo zip || echo tar.gz)"
case "$OUT" in
    /*) OUT_ABS="$OUT" ;;          # --out 给绝对路径就照用
    *)  OUT_ABS="$ROOT/$OUT" ;;
esac

# ---------------------------------------------------------------- 待打包路径

# §2.3 点名要用的 run 目录。runs/bench-20260923 是 rank 的输入，
# runs/workbank/* 是 paths / wire / check / gate / audit / compare / ledger / replicate 的输入。
NAMED_RUNS="
runs/bench-20260923
runs/workbank/relay-dsflash-k0
runs/workbank/relay-t03-k0
runs/workbank/relay-t03-k1
runs/workbank/deepseek-k0
runs/workbank/deepseek-k1
runs/workbank/deepseek-k2
runs/workbank/deepseek-k3
runs/workbank/postfix-deepseek-k0
runs/workbank/postfix-deepseek-k1
runs/workbank/postfix-deepseek-k2
runs/workbank/g1k-workbank-greedy-k0
runs/workbank/g1k-workbank-greedy-k1
runs/workbank/g1k-workbank-t03-p05-k0
runs/workbank/g1k-workbank-t03-p05-k1
runs/workbank/g1k-workbank-t03-p05-pr05-k0
"

# §2.3 里非 run 目录的输入：
#   datasets/...normalized/     decontam-700、render-records
#   state_output/sweep_runs_C   state sanity 的 .pth
#   runs/state-check-20260919   state run 的 --root 默认值
#   outputs/...state-tune-...   state probe 的 --corpus 默认值
OTHER_INPUTS="
datasets/workspace-agent-700-20260920/generated/normalized
state_output/sweep_runs/sweep_runs_C
runs/state-check-20260919
outputs/workspace-agent-700-state-tune-textonly
"

case "$MODE" in
    minimal)  CANDIDATES="$NAMED_RUNS$OTHER_INPUTS" ;;
    standard) CANDIDATES="
runs/bench-20260923
runs/workbank
runs/state-check-20260919
datasets/workspace-agent-700-20260920/generated/normalized
state_output/sweep_runs/sweep_runs_C
outputs/workspace-agent-700-state-tune-textonly
" ;;
    full)     CANDIDATES="
runs
datasets
state_output
outputs
bench/workbank/out
" ;;
esac

# ---------------------------------------------------------------- 体积统计

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

human() {  # 输入字节，输出可读体积
    awk -v b="$1" 'BEGIN{ n=split("B KB MB GB TB",u," "); i=1;
        while (b>=1024 && i<n) { b/=1024; i++ } printf "%.1f %s", b, u[i] }'
}

EXIST_LIST="$TMP/existing"
MISSING_LIST="$TMP/missing"
: > "$EXIST_LIST"
: > "$MISSING_LIST"

TOTAL_KB=0
printf '%s\n%s\n' "$CANDIDATES" "$EXTRAS" | while IFS= read -r p; do
    [ -n "$p" ] || continue
    if [ -e "$ROOT/$p" ]; then
        kb=$(du -sk "$ROOT/$p" | awk '{print $1}')
        echo "$kb	$p"
    else
        echo "MISSING	$p"
    fi
done > "$TMP/scan"

while IFS='	' read -r kb p; do
    if [ "$kb" = "MISSING" ]; then
        printf '%s\n' "$p" >> "$MISSING_LIST"
    else
        TOTAL_KB=$((TOTAL_KB + kb))
        printf '%s\n' "$p" >> "$EXIST_LIST"
    fi
done < "$TMP/scan"

# ---------------------------------------------------------------- 清单

MANIFEST="$TMP/MIGRATION-INPUTS-MANIFEST.txt"
{
    echo "RWKV-Agent 迁移基线输入清单"
    echo "生成时间: $STAMP  主机: $HOST  模式: $MODE"
    echo "仓库 HEAD: $(git rev-parse HEAD 2>/dev/null || echo '?')"
    echo "起点 commit: $(git log --format=%h --diff-filter=A -- docs/go-tooling-migration.md 2>/dev/null | tail -1)"
    echo
    echo "工作区状态（非空表示打包时仓库不干净，产物可能对不上起点 commit）："
    if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
        git status --porcelain 2>/dev/null | sed 's/^/  /'
    else
        echo "  (clean)"
    fi
    echo
    echo "== 已打包（$(wc -l < "$EXIST_LIST" | tr -d ' ') 项，合计 $(human $((TOTAL_KB * 1024)))）=="
    while IFS='	' read -r kb p; do
        [ "$kb" = "MISSING" ] || printf '  %10s  %s\n' "$(human $((kb * 1024)))" "$p"
    done < "$TMP/scan"
    echo
    if [ -s "$MISSING_LIST" ]; then
        echo "== 未找到（跳过）=="
        sed 's/^/  /' "$MISSING_LIST"
        echo
    fi
    echo "== 注意事项 =="
    echo "1. state run / state probe 的 --credentials 指向一个私有 JSON（env 名 → 密钥），"
    echo "   不在仓库里。需要的话用 --extra <路径> 一并打包，或单独发。"
    echo "2. M4 的验收会用本地假服务器重放请求，不需要真端点凭据。"
    echo "3. 解压后目录要落在仓库根，即 runs/ datasets/ state_output/ outputs/ 各就各位。"
} > "$MANIFEST"

cat "$MANIFEST"

if [ "$DRY" = 1 ]; then
    echo
    echo "(--list：未打包。去掉该参数即可产出 $OUT)"
    exit 0
fi

if [ ! -s "$EXIST_LIST" ]; then
    echo "错误：没有任何可打包的路径，检查是否在正确的仓库根目录" >&2
    exit 2
fi

# ---------------------------------------------------------------- 打包

EXIST=()
while IFS= read -r p; do
    [ -n "$p" ] || continue
    EXIST+=("$p")
done < "$EXIST_LIST"

# macOS 的 tar/zip 会带 xattr 影子文件，禁掉；顺带排除缓存类垃圾。
export COPYFILE_DISABLE=1

echo
echo "== 打包 =="
if [ "$KIND" = zip ]; then
    rm -f "$OUT_ABS"
    ( cd "$ROOT" && zip -qry "$OUT_ABS" ${EXIST[@]+"${EXIST[@]}"} \
        -x '*.DS_Store' -x '._*' -x '*/._*' -x '*__pycache__*' -x '*.pyc' )
    zip -qj "$OUT_ABS" "$MANIFEST"
else
    tar --exclude='.DS_Store' --exclude='._*' --exclude='*/._*' \
        --exclude='__pycache__' --exclude='*.pyc' \
        -czf "$OUT_ABS" -C "$ROOT" ${EXIST[@]+"${EXIST[@]}"} \
        -C "$TMP" MIGRATION-INPUTS-MANIFEST.txt
fi

SIZE=$(du -h "$OUT_ABS" | awk '{print $1}')
echo "  产出: $OUT  ($SIZE)"
echo "  清单: 请把 MIGRATION-INPUTS-MANIFEST.txt 的内容（或上面的输出）一起发回来"
echo
echo "提示：VPS 根分区约剩 10G。若上面合计体积接近或超过这个数，"
echo "      用 --minimal 只打 §2.3 点名的那些目录，或先确认 runs/ 里没有多余的中间产物。"
