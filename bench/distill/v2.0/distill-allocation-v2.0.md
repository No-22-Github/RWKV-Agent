# v2.0 计划：MiSS 带思考数据试点

> 2026-10-14。版本号约定：**1.x = state 调优数据，2.x = MiSS 微调（改整个基模）数据。** 出题规格见 [authoring-v2.0.md](authoring-v2.0.md)，脚本见 [tools/v20/README.md](../tools/v20/README.md)。

## 1. 为什么另起 2.x

- **思考要干净。** v1.41 的 DeepSeek 老师带着附加规则（b10-suffix）跑，思考里有 736 步在回想这些规则（"the rule says…""keep under 600 chars"）。学生看不到这些规则，把这些思考练进去会得到"凭空引用不存在的规则"的偏差，删句也删不干净（规则可能已经影响了决定却没说出口）。v2.0 老师**不带任何附加规则**，看到的是和学生同一份题、同一份工具目录。
- **思考要每步都有。** v1.41 老师用自动思考，后续步只有约 70% 有思考。v2.0 用 `--chat-thinking enabled`。冒烟实测仍有约 20–25% 的步不带 reasoning（API 侧行为），这些步渲染成空思考块 `<think></think>`。
- **目录不能背。** 1.x 训练时系统提示和工具目录几乎固定（按字母排序、12–14 个），state 之后编造工具名的次数从约 34 涨到约 100（workbank k0），MiSS 容量更大、更容易背目录。v2.0 让题目只声明约束，目录由生成器随机抽、随机排序，老师和学生看到同一份。

## 2. 数据格式变化

| 层 | 1.x | 2.0 |
|---|---|---|
| 题目 | 可选 `offered_tools`（固定子集，按名字排序呈现） | `tool_policy: {must_offer, never_offer}`；跑题前由 `tools/v20/materialize.py` 按题号定种子抽目录、打乱顺序，写进运行副本的 `offered_tools` + `offered_tools_ordered: true` |
| harness | — | `offered_tools_ordered` 让文本目录和原生 tools 数组都按列出顺序呈现（`agent.Options.PreserveToolOrder`）；加载时与建目录时都校验 `tool_policy` |
| wire | `g1k`（不思考） | `g1k-think` = g1k + 真思考 + nudge=think（10-10 think-full 复测的 T 组，现注册为预设，可 `--strict-spec`），决策预算 4096 |
| 训练行 | 一轮一行 | **一步一行**：真思考 wire 的历史只保留动作、剥掉思考，所以第 k 步的思考不会出现在第 k+1 步的提示里。每个监督步单独成行 = 该步看到的完整提示 + 该步输出（思考 + `</think>` + 动作），loss 只在这一步（`eval.BuildCorpusSteps`，rows 检测到 `thinking=full` 自动启用；行的 meta 多一个 `step`） |
| 老师 | DeepSeek flash，带 suffix，自动思考 | DeepSeek flash，**无 suffix**，`--chat-thinking enabled`，work-v2 全目录随机子集 |

上下文与训练量：冒烟 16 题，单步提示中位 2903 / 最长 5453 token；按步切出的行中位 1405 / 最长 2498 token。代价是前缀在同一条轨迹的多行里重复：每条轨迹约 3900 训练 token，800 条轨迹一个 epoch 约 300 万 token。

## 3. 题目构成（试点，940 题）

| 批次 | 题号 | 内容 | 题数 | 出题 |
|---|---|---|---:|---|
| b20s | `<前缀>-2xxxx`（1.x 原号前加 2：cfg-5003 → cfg-25003） | 从 1.x 训练包挑的题，见 §4 | 600 | `tools/v20/pick_cases.py` |
| b20a | 20001–20040 | 缺工具·本地动作：删/移/改名、跑程序、git、装包、改权限（bash never_offer）；14 道对照题 bash 在场并真做完 | 40 | Sonnet 子 Agent |
| b20b | 20041–20080 | 缺工具·外部动作：邮件/消息/日程/会议室/电话/付款/截图/远程系统/工单/打印，先查资料再给草稿 | 40 | Sonnet 子 Agent |
| b20c | 20081–20140 | 目录变小后的替代与降级：无 web 问时效、无 get_weather 问天气、无 bash 做统计、无 data_query 汇总、无 list_files 找文件、无 calculator 算小数、无写文件工具改文件 | 60 | Sonnet 子 Agent |
| b20d | nt-21001–21200 | 日常问答：HF `dengxiaodi/deepseek-v4.1-flash-distill-zh-2k`（CC BY 4.0）选 200 题，只用题面，在我们的环境里重答 | 200 | Sonnet 子 Agent |

各批出题报告在 [reports/](reports/)。

## 4. b20s 选题规则（pick_cases.py）

- 池子：v1.41 训练包里有通过路径的题（2578 道），去掉从测试题派生的 base700（80）、1.x 终答超过 400 字或带 Markdown 的（253：没有 suffix 后这些最容易答长）、verify.py 钉死 `offered_tools` 的（19）。
- 配额（种子 20261014，每个题族只取 1 道）：bash/天气（v1.41 b12）90 → 多轮 120 → 首轮零调用单轮 120 → 其余按场景填满，单场景不超过公平份额的 1.5 倍。
- 结果：600 道；多轮 140、首轮零调用 164、中文 353、600 个题族；场景 notool 126 / tabular 90 / config 88 / hybrid 74 / logs 69 / docs 60 / web 44 / filesystem 23 / code 18 / script 8。完整名单 [reports/b20s-selection.json](reports/b20s-selection.json)。
- `tool_policy`：must_offer = 1.x 通过路径用过的工具 + required_tools + forbidden_tools（陷阱要在场才算陷阱）；1.x 题若写过 `offered_tools`，被它排除的 work-v1 工具进 never_offer（52 道）。
- 去掉隐性字数上限：题面没有字数/简短要求的轮次删掉 `max_output_chars`（474 处）。冒烟里 6 道失败有 4 道是"题面没说、判据限 300 字"；长度改由过滤器统一卡 600 字。

## 5. 目录生成（materialize.py）

work-v2 共 14 个工具。每题：45% 全目录、35% 删 1–4 个可选工具、20% 紧凑（must_offer + 1–3 个，must 为空时 2–4 个），然后整体打乱。940 题试抽：全目录 / 删减 / 紧凑 ≈ 357 / 299 / 184（840 题时），目录大小中位 12。种子 = sha256("v2.0-toolset:" + 题号)，重跑逐字节一致。

## 6. 过滤（filter.py，跑完老师后、渲染前）

整条路径丢弃，不修补：终答超长（Agent 600 字，日常问答 2500 字）；用户明确只要值时终答带 Markdown；终答语言与题面不符；单步思考 > 3000 字或整条 > 12000 字；思考谈论自己的指令/系统提示/示例/测试；终答里漏出 `<think>`、`<tool_call>`。

**Markdown 口径（用户 2026-10-14 定）**：需要排版的内容用 Markdown（表格、加粗、代码块）是加分，不丢；只有"只回答数字"一类题例外。

## 7. 冒烟（16 题，2026-10-14）

- 通过 10/16；失败 4 道是隐性字数上限（已在 §4 去掉），1 道 bash 在场时 `cat` 代替了 required 的 read_file，1 道澄清题老师擅自写了文件。
- 60 步里 45 步有思考；耗时 26 秒（并发 16）；每题提示合计约 1.1 万 token（每步重发历史，大部分是缓存前缀），生成约 700 token。
- 过滤后 9/10 条保留（1 条思考里谈"system prompt"），按步渲染出 21 行，0 拒绝；训练行里的目录确实是打乱后的顺序。

## 8. 待办

1. 全量老师：`run_teacher.sh` 每批 k=2，`render.sh` 抽每题 1 条路径 → 过滤 → 按步渲染。
2. 收尾打包（待写 `finalize_v20.py`）：终答步的行在末尾加 `\n\nUser:` 并纳入 loss（1.x 终答无 EOS 的教训）；按题族哈希切验证集；`corpus pack`。
3. 目标：Agent 约 600 条轨迹 + 日常问答 100–200 条；MiSS 微调后对照"基模 + 真思考"（workbank 11.3/148），看 workbank、bfcl、bashprobe/weatherprobe。有效再扩量。
4. 已知不足：老师原生模式的系统提示与学生的 g1k-think 文本不完全相同（原生模式有自己的工具说明段），过滤器的 reasoning_meta 规则兜底；一部分步 API 不返回 reasoning。
