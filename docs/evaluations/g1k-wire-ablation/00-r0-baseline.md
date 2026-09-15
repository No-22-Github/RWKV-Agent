# G1K wire 消融 R0：干净基线（2026-09-15）

> [← 返回消融总结](wire-ablation-g1k-summary-20260915.md) | 下一轮：[R1 标签对齐 →](01-r1-align.md)

分支 `ablation/g1k-format`。目的：格式/调用约定消融（R0–R4）的起点——在 G1K 上用当前
wire 原封不动跑 bfcl-product 60 题三遍，拿三类拆项分数和三遍波动，重排后续砍除顺序。
老模型（g1j）上的分数全部作废。

## 配置

- 模型 `rwkv-g1k-7b-temp-3601`（http://100.64.0.1:18222，后端 rwkv_lightning_cuda）
- `--completion rwkv-lightning-cuda --api-url http://100.64.0.1:18222/v1/batch/completions
  --api-stream=false --api-stop-tokens none`（实测该端点拒绝文本形态 `stop_tokens`：HTTP 500；
  与 api-7b 同样只能 `none`，停止全靠客户端截断）
- `--suite bfcl-product --profile xml-v1`（canonical
  `format=xml;transcript=product;transport=text;thinking=off;prefill=none;abstain=none;terminal=none;route=none;catalog=full;control=base;...`）
- 无 state（基模零状态）；`--case-parallelism 60`；二进制在 HEAD f87c89f 重编
- 产物：`runs/ablation-g1k/r0-baseline-run{1,2,3}`；分析脚本 `scripts/ablation-run-report.py`

## 结果：三遍完全一致，波动 = 0

| run | task_success | answer | irrelevance | missing-required | multiturn | model_calls | tool_calls | forced_answers | duplicates | tool_errors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| run1 | 40/60 | 60/60 | **0/20** | 20/20 | 20/20 | 287 | 207 | 58 | 57 | 97 |
| run2 | 40/60 | 60/60 | **0/20** | 20/20 | 20/20 | 287 | 207 | 58 | 57 | 97 |
| run3 | 40/60 | 60/60 | **0/20** | 20/20 | 20/20 | 285 | 205 | 58 | 58 | 99 |

- 三遍间 **0 题翻转**（逐题 task_success 完全一致）；逐题首步 decision prompt 字节数
  三遍相同（中位 1974 B）；总请求字节差异（812924 / 813708 / 803688）全部来自每个
  case 独立 workspace 的临时目录路径长度，不是行为抖动。
- **结论：这台端点贪心解码在本套题上确定性。按预定纪律，R1 起每轮只跑 1 遍。**
- 对照（g1j，runs/xmlstate-ab/base，仅参考、已作废）：39/60，irrelevance 1/20、
  missing 18/20、multiturn 20/20。G1K 把 missing-required 修满了，answer 阶段 60/60。

## 失败全部集中在 irrelevance，且是同一种形状

20/20 全挂，全部同轨迹：模型把"无工具需求"的问题改写成工具任务（发明
`triangle_area.py` 之类的不存在文件名）→ search/read（报错）→ list_files → 重复
发明文件 read → 触发 "duplicate tool call rejected" → 6 步打满 → 强制 answer。
**零主动弃权**：每题 3–5 步全在发 `<tool_call>`，没有一个 case 直接文本作答。

irrelevance_0 轨迹（run1）：

```
1 search_text{query:"area triangle base height",...}   → 命中 0
2 read_file{path:"triangle_area.py"}                   → no such file
3 list_files{path:"."}
4 read_file{path:"triangle_area.py"}                   → no such file（重复）
5 list_files{path:"."}                                 → duplicate rejected
6 (answer) "The provided file triangle_area.py does not exist..."
```

被违反的训诫正是 R2 的候选靶子：`Never invoke tools merely because they are
available`（20/20 违反）和 `questions that do not need new tool evidence must be
answered directly`（20/20 违反）。R3 的 `你好→直接回答` no-call 示范也是冲着这一类。

## prompt 字节数（后续每轮同口径记录）

- 首个 decision prompt：中位 **1974 B**（固定前缀 + 当轮用户问题；其中系统提示词 +
  训诫 ≈0.6 KB、目录 ≈0.55 KB、示例块 ≈0.5 KB）。
- 全 run 所有请求字节合计 ≈ **0.81 MB**（answer 阶段带全 transcript 重发是大头）。

## 对 R1–R4 顺序的影响（按约定，跑完停下，待定夺）

1. **R1（标签对齐）不动**：仍排第一。理由不变——后面语料要按对齐后格式洗，得先钉死；
   且它不依赖 R0 分布。
2. **R2/R3 的靶子变了**：G1K 的全部失分都在"该弃权不调工具"，missing/multiturn 已满分。
   - R2 的"规则写了但错误照样发生"筛选法命中的条目就是上面两条
     （`Never invoke tools merely because...` / `...answered directly`）；砍掉它们
     不太可能修复 irrelevance，但符合"买薄 harness"的目标。
   - R3 的价值上升：no-call 示范是唯一直接示范"不调工具"的 few-shot；但同样别指望它
     单独救回 20 题——示范里没有"问题可解但不需要工具"的对照样本。
   - 若目标是先找回 irrelevance 分数，值得在 R2/R3 之间插一轮"`abstain=no-tool`
     出口"实验（g1i 上 no_tool 被证伪，G1K 未测）；这属于原计划外的新变量。
3. **R4（两阶段合一、去 `<answer>`）的风险面前置了**：answer 阶段在 G1K 已 60/60，
   R4 砍坏的就是这 40 个满分 case 的交付面。开工前必须先定终答停止机制（写进语料的
   行为，不能 harness 单方面定）。
