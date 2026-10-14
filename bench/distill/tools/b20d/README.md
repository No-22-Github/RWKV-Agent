# b20d 出题脚本（v2.0：日常问答批）

`python3 build.py` 从 `local/datasets/hf-deepseek-v41-flash-distill-zh-2k/data/train.jsonl`（2000 行单轮中文问答）确定性地选 200 题，
写成 `bench/distill/v2.0/cases/notool/nt-21001 … nt-21200`，并生成报告 `bench/distill/v2.0/reports/b20d-authoring.md`。固定种子，重跑逐字节一致。

用途：MiSS 微调整个基模后，日常短答容易遗忘。把这些问题放进同一套系统提示词 + 随机工具目录 + 空工作区，让老师重答，
教模型“不需要工具的问题就直接回答；真要精确计算时才调 calculator”。只用源数据的 `instruction`，其 thinking/response 不使用。

选题规则（细节与计数见报告）：completion_tokens ≤ 2048；排除时效题、需要本地文件/个人数据的题、题面含工具名的题；
先抽约 12 道精确计算题，再按 42 个 category 轮转补满，每类封顶 8；8 字符片段 Jaccard ≥ 0.4 视为近似重复并跳过。

每题：场景 notool，files {}，web_fixture []，单轮，不写 tool_policy / tools / max_output_chars；
唯一的 expect 是 `output_excludes: ["UNKNOWN"]`（加载器要求每轮至少有一条期望，这条不约束工具与长度）。
质量由跑完老师后的过滤把关。

自检：

```bash
python3 build.py
RWKV_LAB=local/bin/rwkv-lab-v20 bench/distill/tools/gate.sh v2.0 'nt-21*'
local/bin/rwkv-lab-v20 corpus loadcheck --cases bench/distill/v2.0/cases
```

## 署名（CC BY 4.0）

题面来自 Hugging Face 数据集 `dengxiaodi/deepseek-v4.1-flash-distill-zh-2k`（作者 dengxiaodi，许可 CC BY 4.0，
教师模型 DeepSeek-V4.1-Flash），https://huggingface.co/datasets/dengxiaodi/deepseek-v4.1-flash-distill-zh-2k 。
每个 case 的 tags 带 `source_dataset`、`source_id`、`source_category`、`license: CC-BY-4.0`。
用这批题训练出的模型/数据集发布时，需在说明里保留以上署名。
