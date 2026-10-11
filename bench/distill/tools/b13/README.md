# b13：v1.4 最小补充批次

针对 2026-10-11 的放量复核，采用独立题源，不改存量轨迹。出题 27 道，23 道在库、4 道下架；最终 18 道题提供 40 行。完整验收见 [报告](../../v1.4/reports/b13.md)。

- `build.py`：使用共享 `casegen.Batch` 重建题目、独立校验器、NOTES 和下架状态。初始 24 题及其返修，另补 3 道有列说明的表格任务。只生成题，不生成老师答案。
- `report_stats.py`：复用 `v14_composition.main()` 的同一计数口径，临时增加 b13 rows 输入，输出原始/返修 pass@3、路径剔除和全集前后值；不修改已有统计脚本。
- 老师脚本：`bench/distill/v1.4/teacher/b13.jsonl`，按当前题目版本从 `corpus paths` 产物选取；剔除只走 `common/exclude.jsonl`，不改老师答案。

```bash
python3 bench/distill/tools/b13/build.py
# 对本批 case 目录运行共享 lint、verify --strict-shape、loadcheck、dedup，
# 再做 workbank/live+shelved、p13、v1 shelf、bashprobe、bfcl-product 去污染。
# 不用 gate.sh 的 || true 作为 lint 验收依据。

# 在 shell 中加载用户配置；不得输出 key 或使用 set -x。
source ~/.llm_api_key.sh
export API_KEY
# 各版本题用独立 cases 快照；每组 k=0,1,2，输出目录不能复用。
local/bin/rwkv-cli agent-eval --completion chat-completions \
  --api-url "$API_BASE/chat/completions" --api-key-env API_KEY --model "$MODEL_NAME" \
  --chat-token-limit-field max-completion-tokens --chat-thinking auto \
  --temperature 0.3 --top-p 1 --include-draft --cases <本批题目录> \
  --tool-catalog work-v1 --file-tools lines --max-steps 16 --max-tokens 4096 \
  --decision-max-tokens 8192 --case-parallelism 8 --case-timeout 30m \
  --chat-system-suffix bench/distill/v1.4/teacher/b10-suffix.txt --output <新的run目录>

# corpus paths 每题上限沿用默认 2；按题版本合并，不改 outputs。
local/bin/rwkv-lab corpus render --cases bench/distill \
  --script bench/distill/v1.4/teacher/b13.jsonl --source distill-b13 \
  --rotate-catalog 0.4 --out <新的corpus目录>
python3 bench/distill/tools/b13/report_stats.py --json <统计输出.json>
# suffix -> 原有按 case ID 的 split -> pack --exclude -> to_segments -> segcheck
```

本次本地工作目录为 `local/runs/distill/v141/b13/`：`teacher-k0..2` 是初始 24 题，`fix-k0..2` 是 14 道 v2，`extra-k0..2` 是新增 3 题，`extra-fix-k0..2` 是 tab-8806 v2。版本选择关系与原始快照已存本地。直接重建当前题再跑 k=3 即可生产新的当前版本路径；采样不可复现，已入库老师脚本可确定性重放。
