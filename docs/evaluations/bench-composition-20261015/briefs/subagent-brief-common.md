# 补题子任务通用说明（Sonnet 批，2026-10-15）

你是出题 Agent。仓库根目录 `/Users/no22/Projects/RWKV-Agent`。用中文写报告。

## 必读（按顺序）
1. `docs/evaluations/bench-composition-20261015/gap-fill-spec.md` —— 实施规格书，硬约束全在这里，§2.1 题目结构、§2.x 你那一批、§4 坑、§5 命令。
2. `docs/workbank/authoring-guide.md` —— 陷阱 ID（§3）、axes/level（§3、§4）。
3. `bench/workbank/tag-vocab.json` —— scenario / task_type 只能用这里登记的值。
4. 两份前轮试点报告（重点看"主审发现"和失败归因，别再踩）：
   `docs/evaluations/bench-composition-20261015/gap-fill-report-pilot30.md`、`gap-fill-report-sol20.md`。
5. 参考样题：`bench/exam/pilots/sol-20261015/cases/` 下的 20 题（结构、verify.py、NOTES 写法）。需要 web / 多轮 / 大 fixture 等写法时，到 `bench/workbank/cases/`、`bench/exam/imported/`、`bench/bashprobe/` 里找现成例子照抄字段名，不要猜字段。

## 与规格书不同的地方（以这里为准）
- **编号**：不用 6xxx（已被占）。用你任务里给的号段，`<缩写>-<5位数>`，例如 `log-13101`。号段内从小到大连续编。
- **目录**：题放在 `bench/exam/pilots/sonnet-20261015/<你的批次名>/cases/<scenario>/<id>/`，**不要**放进 `bench/exam/cases/`（那里会自动并入考卷）。
- **author**：`"llm:claude-sonnet-5-5"`；`status: "draft"`；`reviewer: null`。
- **不做 M4**（不跑 exam build、不改 full.json/quick.json/SUITES.md）。
- **盲解并发**：`--case-parallelism 6`（同时有 6 个出题 Agent 在跑 DeepSeek）。输出目录 `local/runs/exam-gapfill-sonnet-20261015/<你的批次名>-deepseek-r<轮次>`。
- **不要 git commit / push / 切分支**。不要改 `internal/`、`cmd/`、旧题、其他批次的目录。不要 ssh 任何机器。

## 用户最在意的一点：题面要像真人说话
上一轮复核的头号问题是题面像元指令（例：「我需要你处理 version，但没有提供具体路径。先向我询问路径，不要调用工具。」「Directory listing and text search are forbidden」「Answer exactly 'X=N'」）。你的每道题面都要过这一关：**想象一个普通用户在聊天 App 里打字**——口语、可以有背景、可以有点随意，但绝不写工具名、步骤、输出格式模板、"不要调用工具"、"如果不存在就说没有"、对陷阱的提醒。要单个值就说「直接告诉我数字就行」这类人话。写完每题自查一遍题面。

## 前两轮踩过的坑（照做）
- 自由措辞的产物不要用全文 `equals`（排版/标题/空格会误判）；要么给出固定模板让模型填，要么钉关键原文 `contains`。
- 全文 `equals` 小心末尾换行；配置合并类题要考虑无最终 LF 的合法写法。
- 同一路径的文件检查不要混用 `unchanged` 和 `contains`/`equals`（loader 会拒绝整套）。
- 非目标输入文件要加 `unchanged: true` 保护，防止改坏源数据也能过。
- 反问题（ambiguous_request）不要锁完整话术，只钉反问要点的同义词组（`output_contains_any`）。
- 拒绝/做不到题，`output_excludes` 不要放「已发送 / has been sent」这类成功短语——否定句「我不能说已经发送」会被误伤。用 `forbidden_tools` 防假装完成。
- smalltalk 与 bank lint 有冲突（lint 要求非空 output_contains_any）；遇到就在报告里记录，不要为过 lint 硬塞关键词。
- `bank verify` 的破坏探针对「答案来自用户消息」的题会误报 FAIL（改坏旧文件答案理应不变）。这种情况**记录即可**，不要为了过探针加无关断言。
- 数字题问法要逼出一个结论；干扰值不要是解释时顺手会提的中间量。
- 题面日期、fixture 路径、expect、verify 要同步；固定时钟 2026-09-16。

## 流程（规格书 §3、§5 的精简版）
1. 先写 NOTES.md，再写 case.json（用 Python `json.dumps(..., indent=2, ensure_ascii=False)` 生成，不要手拼）和 verify.py。canary：`EXAM-CANARY-<8位小写hex>`，每题唯一，description 结尾 / verify.py 首行 / NOTES.md 末行三处一致。
2. M1：
   ```
   local/bin/rwkv-lab bank lint --cases <你的cases目录> --canary-prefix EXAM-CANARY
   local/bin/rwkv-lab bank verify --cases <你的cases目录>
   ```
   二进制已编好，不要重编。lint 必须 0 violation；verify 的失败只允许是上面说的"答案来自用户消息"那种探针误报，并逐题写明。负向测试做一次（隔离副本里改错一道数字题的 expected_number，verify 必须 FAIL）。
3. M2 盲解（DeepSeek）：
   ```
   source ~/.llm_api_key.sh && export DS_KEY="$API_KEY" RWKV_JUSTBASH_SIDECAR=$PWD/local/bin/justbash-sidecar
   local/bin/rwkv-cli-chat agent-eval --completion chat-completions --api-url "$API_BASE" --model "$MODEL_NAME" \
     --api-key-env DS_KEY --chat-thinking disabled --temperature 0.3 --top-p 1 \
     --cases <你的cases目录> --include-draft --harness app \
     --case-parallelism 6 --remote-batch-wait 0s --output local/runs/exam-gapfill-sonnet-20261015/<批次名>-deepseek-r1
   ```
   （shell 是 fish；上面这段请用 `bash -c '...'` 包起来跑。）跑完逐题读失败题的轨迹和回答，归三类：题有问题→修题后只重跑修过的题（新输出目录 r2）；DeepSeek 真不会→NOTES 加 `## Teacher result`；harness 问题→记录。最多修两轮，不要为了分数放宽判分。通过的题也抽读几道，确认不是蒙对。
4. M3 去污染：
   ```
   for v in v1 v1.3 v1.4 v1.41 v1.42 v2.0; do [ -d bench/distill/$v/cases ] && local/bin/rwkv-lab corpus decontam --test <你的cases目录> --candidates bench/distill/$v/cases | head -1; done
   ```
5. 交付：写 `docs/evaluations/bench-composition-20261015/gap-fill-report-sonnet-<批次名>.md`（中文，白话，代号第一次出现时解释）：题目清单（ID、task_type、难度、一句话题意）、分布对照、lint/verify 结果、盲解成绩与逐题失败归类、去污染结果、发现的旧题或检查器问题。

最后给主 Agent 的回复控制在 15 行内：题数、lint/verify、盲解成绩（各轮）、"题有问题"是否清零、报告路径、需要主 Agent 决定的事。
