# G1K 两枚已有 state 的格式对齐与评测（2026-09-19）

结论：两枚 state 已上传并完成全套高并发主对照。修正两个真实格式差异后，Workbank 没有端到端提升；fast state 在 BFCL product 上的局部收益经复测方向一致（29→33、28→34），但主要来自抑制不必要调用，伴随拒答与退步，不能等同于推理能力提升。没有重新训练。

## 研究设计

用户提供 agent_state_none.pth 与 agent_state_fast_think.pth，均已上传至指定备用 G1K 服务。采用 raw `/v1/batch/completions` 接口（`contents` 字段），显式指定 state_id，不使用 chat 接口的自动 think 模板。四组主实验分别是零 state/none、none state/none、零 state/完整 fast-think、fast-think state/完整 fast-think。每组三套件：Workbank 40、Boundary 18、BFCL product 60。后者不是官方完整 BFCL 榜单。

用户随后明确指定集群高并发，正式主对照改为同套件全部 case 并发：Workbank 40、Boundary 18、BFCL 60，使用 -high 目录名，四组同条件。此前并发 4/串行运行保留为补充诊断，不与高并发主表混算。采用同一套 Agent 执行逻辑、非流式、top_k=1、temperature/top_p=1、penalty 0/0/1、max_steps=10、rescue 关闭。保留默认实际阶段预算（512/1024），不叠加上轮已无端到端收益的 2048 改动。每个套件前后各做两个固定 raw 请求；保留响应和哈希、服务端 state 登记，网络错误或指纹不稳定的 run 不作为可靠模型比较。

## State 与训练文件身份

- none state SHA-256：`e154256321eaf11006a28b7920191be3d3c8bf672c17497640163f8a0a373484`。
- fast-think state SHA-256：`ead1fcc609346f4869a0a5ab015f3378c4de7a2140dc9f05ca21e4563a5139c7`。
- 只读检查 zip storage 与 pickle opcode（不执行反序列化代码）：两份均为 32 层 att.time_state、8388608 个 float32，非有限值为 0，所有元素非零。此检查不替代加载后的任务评估。
- 服务端两文件各 33562656 字节、32 tensors；state ID 为原文件名，没有覆盖既有同名文件（上传前列表为空）。
- none 训练集 SHA-256：`d3d533ab8d146de2464733ef6c539efc09ba5bc86739d8332029c7d6b98c450b`。
- fast-think 训练集 SHA-256：`3a51de865a048af4f3038390c08e266bb34febc778bd285cea6e29439fbf091a`。

真实文件摘要保存在 experiment.json 的 state_file.sha256。CLI run.json 中的 state_sha256 可能只是 ID 字符串摘要，不混用。服务端没有提供加载 tensor 的内容摘要；本地哈希、上传回执、登记和行为指纹组成可核查证据，不能称为服务端字节证明。

## 全量格式审计

两份训练导出均为 2494 条、7537 个 assistant 段。按相同 ID 配对，去除 fast 版每个 assistant 段的空 think 后，2494/2494 条文本逐字相同。两份监督内容数量相同：4222 个工具调用、3315 个普通文本回复。

- none：assistant 不带 think。
- fast：7537/7537 个 assistant 段都以 `<think></think>` 开始；loss_spans 起点在这个前缀之后，前缀是给定上下文。
- 0 条旧 Tool: 角色，0 条 `<no_tool>` 伪标签，0 条 WORKBANK-CANARY；这些检查不等于证明没有其他形式的数据污染。
- no_tool 虽在目录中，却有 **0 次监督调用**；终答训练主要使用普通文本，不应假定 state 学会 no_tool 出口。
- 当前工作区工具的直接示范极少：read_file 仅 1 次；list_files/search_text/web_search/web_fetch/data_query/calculator/write_file/append_file 均 0 次。不能把同类语义但不同名称的工具也算为零，本统计只计精确名称。

发现旧 fast-think 实验只对当前生成加前缀，已执行工具写回历史时变成不含 think 的规范调用。对所有 7537 个训练生成位置重建历史，旧 renderer 有 **5043 个字节前缀不匹配**。新增显式 `history=think-fast` 后，两份训练集各 7537 个位置均与训练文本对应前缀逐字相同，真实 RWKV tokenizer token 前缀也全部相同。none 生成末尾保留 Assistant:，fast 保留 Assistant: <think></think，保留下一 token 的合并边界。

另一个差异是训练 fast 导出仍使用 none 版 System 控制句，旧 think-fast profile 会把它换成另一条指令。主对照为 fast 两组共同指定 `history=think-fast,thinkcontrol=off`，其中后一个独立轴恢复训练句。格式对齐组合包含这两项，不能把之后的涨跌只归因于历史前缀。

早期低并发诊断曾跨过一次 binary 重建；最终 12 组 `-high-` 主对照与后续复测全部使用同一 binary：`91ba7c47403695d71bcbf3b9f7d42212dd028d5fe6dda80ebf80cbcc415b9138`。同格式 state A/B 的首步 prompt 逐题一致（40/40、18/18、60/60），采样、wire 和 case ID 均一致；仅 state ID 不同。none 与 fast 的跨格式对照明确不是单独 state 效应。

这纠正了旧报告“只检查当前生成开口就认定整体命中训练分布”的过强结论。对齐开关只改变历史前缀与上述控制句，不自动改变工具选择、工具结果、强制收尾或答案判分。训练与实战的工具集、用户任务、执行错误和运行控制提示仍不同，不能把字节格式对齐称为整体语义分布完全对齐。

## 高并发主结果与有效性

| 组别 | Workbank 40 | Boundary 18 | BFCL product 60 |
|---|---:|---:|---:|
| 零 state / none | 3† | 0 | 49† |
| none state / none | 0 | 0 | 23 |
| 零 state / fast 完整对齐 | 1† | 1† | 29 |
| fast state / fast 完整对齐 | 1 | 2† | 33 |

这是原始判据的实测通过数，不是重新判分。BFCL product 是项目的 60 题产品适配子集，不是官方完整 BFCL 榜单。所有 12 组传输错误均为 0，服务端 state 登记稳定；所有固定探针在实际客户端停止边界之前的有效文本一致。

† 标记整组前后 **raw canary 完整输出哈希发生变化**：差异在既有客户端停止标记之后（例如工具调用之后编造的工具结果，或问候之后编造的下一轮 User）。原始严格有效性 `valid_for_model_comparison=false` 保留，未为了接受成绩而放宽或覆盖。`canary_effective_stable=true` 只是新增诊断字段。因此主表可以报告观察值，但带 † 的比较不能称为通过原始严格漂移校验的因果证明。fast BFCL 的 29→33 两组均通过严格校验；Boundary 的 1→2 首轮没有。

主轮耗时：Workbank 四组约 251/148/226/170 秒；Boundary 68/91/128/80 秒；BFCL 86/87/81/86 秒。none BFCL 早期串行诊断约 1489 秒，60 并发约 87 秒；串行 22/60、高并发 23/60，不能宣称每条输出完全确定。集群并发设置符合用户建议，未发生主轮网络失败。

### Workbank：所有 36 道需要工具的任务仍然失败

零 state / none 通过 nt-0002、nt-0003、nt-0004；两组 fast 均只通过 nt-0003。none state 四道 no-tool 题都调用了工具，全部失败。fast state 虽四道都不调用工具，但 nt-0001 输出 90（期望 9000），nt-0002 输出 https（期望 443），nt-0004 输出不满足答案契约的 “I cannot determine”；只有允许弃权的 nt-0003 通过。

同格式 fast A/B 没有任何通过/失败翻转。重复调用拒绝 20→13、强制收尾触发 26→14，看似改善；但 36 道需要工具的题中完全没有实际工具调用的题数 10→19。工具尝试后自主终止仅 2/29→2/17。减少重复的一部分代价是提前放弃，不能将其当作成功率提升。

none state 的首步来源机械正确率为 26/40，28 道纯本地题首步误搜网页为 0，首步未解析为 0；但重复调用拒绝 29，强制收尾 29，answer 阶段仍调用真实工具 34 次（17 题），最终 0/40。这说明选对来源和完成整个任务之间仍有较大落差。

### BFCL：fast 的净 +4 来自哪些题

| 子集 | 零 state / none | none state | 零 state / fast | fast state |
|---|---:|---:|---:|---:|
| 不相关工具，应不调用（20） | 12 | 2 | 1 | 6 |
| 缺参，应澄清（10） | 10 | 0 | 2 | 2 |
| 参数齐，应调用（10） | 8 | 5 | 10 | 8 |
| 多轮状态（10） | 9 | 8 | 6 | 8 |
| 错误恢复（10） | 10 | 8 | 10 | 9 |

fast 同格式比较新通过 11 题、新失败 7 题，净 +4。子集分解：无关工具 +5，缺参 0，参数齐全 −2，多轮状态 +2，恢复 −1。完整翻转 ID 见逐题报告与 state-comparison.json。

这个增益有明确语义限制。三角形面积、最近整数、物理题的新通过回答包含 “I don't have a tool that can calculate ... / answer this question”。irrelevance 验收主要检查不乱调用工具，并不保证问题解答正确；这些通过是弃权行为改善，不是数学能力提升。参数齐全的两道新失败出现额外 reason 字段；恢复题出现裸 JSON，协议层拒绝；另有记住 CHECKSUM-OK 但第二轮格式不合规的失败。

none 缺参 0/10 也不能解释为完全不会识别缺参：部分回答用英语表达缺少路径/关键词，未命中当前中文关键词判据；部分只是叙述“需要问用户”而没有实际发问。原分数保留，语义诊断单独记录，没有偷偷放宽评分。

## 失败机制：哪些是格式，哪些是能力或策略

| 证据 | 诊断 | 不能作出的推论 |
|---|---|---|
| none 的 Boundary 42/TCK-204/MANGO 含正确值，但附带说明文字 | 有局部答案格式损失 | 不能把全部失败都算作格式问题 |
| cfg-0002 回执已有 MAX_CONNECTIONS=950，仍选择 YAML 的 600 | 配置优先级理解/证据取舍错误 | 不是纯粹没有收到答案 |
| code-0003 把 7 个文本命中当成 3 个实际调用点 | 搜索结果到语义计数的转换错误 | 不能只提取一个数字修复 |
| fs-0001 编造 cold_storage_budgeting_by_file_footprint，ENOENT 后重复并宣称工作区为空 | 路径发明、恢复失败、无依据结论 | 不是工作区确实没有文件 |
| scr-0001 宣称 CSV 已正确，但实际仍输出竖线分隔；fast scr-0004 复述任务而未写文件 | 执行和交付缺失 | 终答说“完成”不能替代文件/运行验收 |
| fast 大量工具题直接 UNKNOWN / cannot determine | 过度抑制行动 | 不是更可靠完成，也不是所有题都该弃权 |
| 退款题同时出现 47.80 和 4780 的解释 | 内容自相矛盾 | 不能按正确数字的子串存在就安全抽取 |

主轮 receipt 审计仅 zero-fast Workbank 有两条机械未匹配；逐条查看均为 web-0004，第 4→5 和 7→8 步。真实错误回执实际存在；前面的模型输出伪造未闭合 tool_response，导致审计正则吞掉后面的真实标签。这是诊断器的标签匹配局限，不是两条回执被客户端丢弃。其余主轮已检查回执均匹配。保留原机械统计，不将两处误报用于模型归因。

## 对“是不是一直没有发挥出模型能力”的判断

**确实存在接入损失，但本次证据不支持“只要对齐这两个 state，就能解锁强端到端能力”。** 历史 think 前缀与 System 控制句是实在的偏差，现在已经显式对齐并完成全量 token 检查；对齐后工具任务仍未通过。与此同时，有正确值却因严格格式失败的题，也有 evidence 已齐全但语义理解错误、未实际交付文件的题。两类问题同时存在。

这两份训练导出去掉空 think 后内容完全相同；fast 不是带有显式推理过程监督的另一个推理数据集。空 think 前缀表示给定的格式，不能仅凭文件名把它视为训练出了更强推理。none 与 fast 的不同 state 效果需要实测，不能只由前缀差异推断。

训练中本项目工具的精确名称覆盖稀薄，以及 no_tool 在目录中却没有监督调用，提供了行为迁移不稳的合理解释，但不是已证明的唯一原因。此次没有重新训练，也没有检查完整训练过程、优化器或训练日志，因此不能断言具体训练环节坏了。

当前不建议把任一 state 设成产品默认，也不建议全局强制空 think。后续无训练路线应优先验证：

1. **答案出口单轴对照**：普通文本与 no_tool/final-answer 出口分开，保持同一题目、prompt 其余部分与预算，完整跑原套件；只认可实际新增通过，不能把 parser 接受率当成绩。当前训练普通文本终答远多于 no_tool 监督，值得优先测试，但尚未证明有效。
2. **证据已足够时的终止/作答能力**：延续上轮 evidence-only 诊断与原 40 题分别记分。条件探针用于区分证据检索与证据理解，不能代替真实 Agent 成绩。上轮实给 2048 并未改善原 40 题，此次不重复堆预算。
3. **工具错误后的真实恢复**：限定一个完整且无歧义调用的解析恢复，保留权限和参数校验；不可将前言后任意 JSON 都执行。格式修复与任务内容错误独立计数。
4. **保留正确性与交付验收**：严格数字/语言约束可另做语义诊断，但文件生成、脚本运行、配置优先级等不能靠松评分“提分”。

以上是依据失败证据排序的下一轮假设，不是本轮已验证的提分方案，也不是对模型能力上限的证明。

## 补充运行与保留边界

早期并发 4/串行诊断保留，主表只采用同条件 -high 组。none-state-boundary 早期 4 道 unexpected EOF 不进入成绩比较；前后 canary 一致不能抵消传输失败。none 低并发 Workbank 0/40，fast 低并发且已启用完整对齐的 Workbank 1/40，与主轮相同；none 串行 BFCL 22/60、Boundary 0/18。所有未通过严格指纹检查的运行均保留原记录，不以重跑覆盖。

## 有边界的高并发复测

完成固定 7 组复测；加上 12 组主矩阵，共 19 组、768 次 case 评估（包含重复题，不是 768 道独立题），全部没有传输错误。到此停止，不循环重试至获得目标分数。

| 复测组 | 通过/总数 | 严格原始指纹稳定 | 有效文本稳定 | 耗时（秒） |
|---|---:|---|---|---:|
| zero-none-repeat-workbank | 3/40 | 否 | 是 | 201 |
| zero-none-repeat-bfcl | 49/60 | 否 | 是 | 70 |
| zero-fast-repeat-workbank | 1/40 | 是 | 是 | 197 |
| zero-fast-repeat-boundary | 1/18 | 是 | 是 | 126 |
| zero-fast-repeat-bfcl | 28/60 | 是 | 是 | 86 |
| fast-state-repeat-boundary | 2/18 | 是 | 是 | 78 |
| fast-state-repeat-bfcl | 34/60 | 是 | 是 | 90 |

复测判读：

- 零 state / none 的 Workbank 3/40、BFCL 49/60 通过集合都未变化；原始 canary 尾部仍变化，保留严格无效标记，不以复测相同成绩抵消。
- 零 state / fast 的 Workbank 复测通过严格校验；与 fast-state-high-workbank 比较，两组同 binary、wire、采样及 40/40 首步 prompt，仍 1/40→1/40、零翻转。这是严格校验成立的 Workbank state 对照。
- Boundary 两组复测均严格有效，1/18→2/18；唯一新增仍为 pb_avoid_forbidden_tool，无退步。此前两组均通过的 pb_read_only_repo_explain 保持通过。
- BFCL 两组首次与两组复测均严格有效。首次 29→33（11 新通过、7 新失败），复测 28→34（12 新通过、6 新失败），局部增益方向复现，但仍远低于 none 基线的重复观察值 49/60。
- BFCL 子集复测：irrelevance 1/20→6/20，缺参 1/10→3/10，参数齐全 10/10→8/10，多轮状态 6/10→8/10，恢复 10/10→9/10。无关工具 +5 与两个退步子集保持不变。
- 零 fast 唯一复测掉分 bfcl_missing_simple_python_51：由中文询问关键词变成英文询问，没命中“关键词”字样。fast state 唯一复测涨分 bfcl_missing_simple_python_49：由缺 envelope 的裸 JSON 变为合法 no_tool envelope。两处都不是新学会了解题。
- 这也证明有限固定探针稳定不保证全套题逐 token 确定。没有服务端日志/数值执行证据，本报告不把这类波动归因于特定集群路由、不同 checkpoint 或某个采样实现。

全部原始和复测比较、首步 prompt 一致数、binary/sampling/wire 一致性以及逐题翻转已写入 state-comparison.json。

## 验证与代码范围

新增 opt-in history=think-fast 与 thinkcontrol=off，不修改产品默认值；测试覆盖真实工具动作规范化后的历史、已含前缀不重复、旧默认保持及不兼容 thinking 配置拒绝。全量训练生成前缀与 tokenizer 对齐审计见 renderer-alignment-audit.jsonl；数据结构统计见 training-alignment-audit.json。

验证：`go test ./...` 全部通过（只有已有 macOS 链接目标版本警告）；审计脚本 5 项测试通过；`git diff --check` 通过。没有提交或推送。

## 复现与产物

- 主矩阵脚本：scripts/state-matrix.py；逐组入口：scripts/state-experiment.py（默认全部 case 并发）。提交整理时已移除本次运行专用的固定 PID 等待；复跑仍需使用未存在的新运行目录名。
- 复跑必须使用新目录名以免覆盖；例如 `python3 scripts/state-experiment.py fast-state-new --fast --state-id agent_state_fast_think.pth --suites workbank,boundary,bfcl --credentials /tmp/rwkv-wire-experiment-credentials.json`。
- 汇总：`python3 bench/workbank/tools/state_results.py runs/state-check-20260919 --output runs/state-check-20260919/state-comparison.json`。
- 逐题：`python3 bench/workbank/tools/state_case_report.py runs/state-check-20260919/state-comparison.json bench/workbank/reports/state-case-comparison-20260919.md`。
- 真实请求、输出、得分与 canary：runs/state-check-20260919；敏感 header 通过临时凭据文件/环境传入，报告不含凭据。
