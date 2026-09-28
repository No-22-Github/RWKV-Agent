# Claude 扩题反驳审阅与实验

## 范围与方法

审阅对象为用户提供的 `Claude-Generating training data from workbank questions-20260919-2256.md`。
文档中的建议按待验证假说处理，不视为执行授权或仓库事实。
用户随后提供 G1K API，明确本轮不加载 state，并要求比较不 thinking 与 fast/fake think。

本轮不修改冻结的 40 题、正式评分器或默认 wire。新增脚本位于 `bench/workbank/tools/`；
完整运行数据位于 `runs/scorer-ablation-20260919/`。该目录被 Git 忽略，报告与可复现脚本保留在仓库内。

判据实验采用**同一轨迹配对重判**。`turn.Expect` 在 `internal/agent/eval/runner.go` 中用于生成完成后的
`validateTurn`，并不作为这几个原生 suite 的模型输入。因此判据消融无需分别向模型发出三次请求；
三次独立生成反而混入采样/服务端波动。新鲜 API 运行用于更新基线和比较 thinking，重判用于隔离评分变化。

- B-V2：原判据；B-V1：仅 `output_equals` 改字符串包含；B-V0：进一步忽略 `required_calls` 与 `forbidden_tools`。
  原来那道 `expected_number` 题在 Boundary 消融中保持数值判据不动。
- W-V3：原判据；W-answer：等值字符串改包含，数值输出改完整数字 token 容差。
  另设独立的 no-UNKNOWN 臂与组合臂，避免把放宽和收紧两个方向混成一次归因。
- 所有重判保留运行错误、协议/答案契约修复、required_tools、文件状态、脚本执行与未完成回合等失败。
  使用各次 `run.json` 冻结的题目，不拿当前题目覆盖历史；原判据必须能逐题重构原始通过状态。
- “任一数字命中”和 contains 是宽松诊断，不是语义正确性证明，更不是模型能力提升。
  例如同时出现正确数字和相互矛盾的结论也可能命中；脚本保存所有候选数字和原答案供复核。

## 仓库核验：哪些论证成立，哪些不成立

| Claude 的断言或建议 | 核验与判断 |
|---|---|
| Boundary 18 道全部 `output_equals` | 错。16 道等值、1 道 `output_contains`、1 道 `expected_number+tolerance`；历史 manifest 与当前源码均如此。 |
| BFCL 高、Boundary 低，所以判据是主因 | 跨 suite 同时改变任务、语言、工具约束、回合数等因素，不能据此归因。配对重判确有局部收益，见实测表。 |
| `required_calls` 是完整精确参数匹配 | 不准确。Go scorer 的 `argumentsContain` 检查所需字段，允许额外字段；删除调用要求仍只是一项诊断。 |
| 删除 `forbidden_tools` 后能涨分便证明 harness 太严 | 不成立。`pb_avoid_forbidden_tool` 的用户题面明确禁止 listing/search，删约束会放过真实违约。 |
| 删除 UNKNOWN 后 3/40 应变 1/40 | 历史记录不支持。nt-0004 实际是 `720 GB per day`，仍满足其数字分支；只删除 UNKNOWN 得到 2/40。 |
| nt-0003 拒绝就通过是错误 | 不能这样概括。该题要发邮件，但目录没有邮件工具，正确拒绝正是目标；UNKNOWN 是否信息不足值得修订，但不应取消能力边界评估。 |
| nt-0004 判据存在缺口 | 成立，但不只 UNKNOWN：`720` 本身也不要求解释无法发消息，数值正确与交付诚实应分别验收。 |
| 改成判文件状态可以解决字符串问题 | 方向合理，但仓库早已有 `CaseExpect.Files/Run`；cfg/doc/hybrid/script 多题在做文件或脚本验收。不能说执行验收尚未存在，也不能用一句“完成”覆盖它。 |
| 原 harness 能过而当前不过，就一定是 harness；都不过就一定是模型 | 不成立。若同时换 g1i/g1k、量化/后端、prompt、工具模拟器及 wire，无法归因。需要同模型同 fixture 的控制对照。 |
| BFCL 产品样本不是完整官方 BFCL | 成立。60 题是产品适配集；其不调用子集主要评估行动选择，不保证数学/知识答案正确。 |
| 自造字符串绝不可能污染、公开题成绩更低即可否定污染 | 证据不足。新标记不证明任务模板没见过，两个难度不同的子集也不能作污染的因果检验。本轮不声称验证了训练数据来源。 |
| canary 不稳就是高并发下题目 description 指纹不稳 | 混淆两种 canary。此前不稳定的是固定 API 探针的 raw 完整输出哈希；报告已说明差异位于客户端停止边界之后，不是题目 description 被篡改。原严格有效性限制仍应保留。 |
| 主指标别用 pass rate | 应同时保留端到端成功率与过程指标。减少循环也可能来自直接拒答；过程改进不能自动替代交付成功。 |
| 16 道每格 2 题能精确找到单一断点 | 适合侦察，不够精确估计通过率或证明因果。两变体同骨架不能当作完全独立的统计样本。 |

统计论证也应降调：不显著不等于“没有提升”；同题比较应看配对翻转，而非仅比较两个总分。
精确双侧 McNemar 在纯增 6、零回退时 p=0.03125，已低于 0.05，并非必须 +7。
“200 扩到 400 只是小数点改善”也不准确：独立同分布的理想条件下，标准误约缩小到原来的 1/√2；
是否值得扩题取决于最小关注效应、变体相关性和出题成本，不能从几条分数直接定为 60/200/400。

## 梯度与目录实验的边界

16 道独立于正式 bank 的诊断题，8 格各 2 个固定变体：P0A0/P0A1/P0A2/P0A3、P1A1/P2A1/P3A1/P4A1。
两条线的原点共用 P0A1。每题 fixture 总计 240 UTF-8 字节，以空白补齐；文件数按路径任务变化。
P3 必须使用 5 个候选，与 Claude 同时要求的“1–3 个文件”冲突，明确记作例外。
P4 不强制必须 search 后再 read：真实 search 回执若已有充分证据，直接回答不该被人为判错。

每种 thinking 都把全部 16 题分别跑默认目录及 work-v1，同题同 prompt 同预算。
这是**目录组成对照**，不能把不同工具能力造成的变化一律叫“纯数量效应”。
默认 4 个实际工具、work-v1 12 个实际工具之外，两组都包含相同的 no_tool 控制出口。

梯度原判据保留 exact answer，同时对同轨迹报告宽判，避免事先用宽判掩盖格式能力。
工具证据指标只表示至少一条实际证据回执，**不证明证据充分**；跨文件题还需看逐题调用。
TERM 从同一轨迹派生：宽判成功、无强制收尾/运行错误/答案契约修复、自主 final/no_tool，且模型生成步数不超过 ref_calls+1。
这与通过率相关，不能称为统计独立的“正交”指标；无需复制新题就能计算。
ref_calls 是诊断设计中的参考预算，并不证明唯一最优路径；例如为稳妥求和多调用一次 calculator
也可能合理。因此 TERM 是额外的紧预算指标，不覆盖原任务通过判据。

## 历史轨迹重判

| 历史 run | 原判据 | 仅答案放宽 | 再删除 required_calls/forbidden_tools |
|---|---:|---:|---:|
| ablation-g1k/final-boundary | 0/18 | 4/18 | 4/18 |
| state-check/zero-none-high-boundary | 0/18 | 5/18 | 5/18 |
| state-check/none-state-high-boundary | 0/18 | 4/18 | 4/18 |
| state-check/fast-state-high-boundary | 2/18 | 6/18 | 6/18 |
| workbank/closeout-v0-g1k | 3/40 | 6/40 | 不适用 |
| state-check/none-state-high-workbank | 0/40 | 2/40 | 不适用 |

旧 Boundary 的新增 4 题是 csv_sum、json_extract、avoid_forbidden_tool、missing_file_recover，人工查看原答案后确有正确值。
旧 Workbank 新增 cfg-0001、doc-0003、nt-0001；none-state 新增 cfg-0001、web-0002。
历史 state 表仅说明**那批输出的评分敏感性**，不解除原报告的服务端指纹限制，也不用于本轮无 state 的因果比较。

## 新 API 实测

API 返回模型 `rwkv-g1k-7b-temp-3601`，不传 state_id；使用本轮从当前源码构建的同一个 CLI。
temperature/top_p=1、top_k=1，presence/frequency=0、decay=1，max_steps=10，rescue 关闭，非流式。
原套件并发上限 40；16 题诊断并发 16。全局 max_tokens=1024，实际 decision/answer 请求为 512/1024。
模型 metadata 与采样留在每次 run.json，binary/case/command 摘要留在 experiment.json。

none 使用 `xml-v1+align-qwen36+no-tool+bare+one-stage`。
fast 在其上加 `think-fast` 和 `history=think-fast,thinkcontrol=off`：固定 System 控制句，
改变当前空 think 前缀及历史 assistant 前缀。这是一组明确的 fast 格式配置，不把它伪称为单独 state 效应。
仓库的字面 `fake-think` modifier 仅适用于 Markdown；不把切换整个协议混进本轮 XML 比较。

| 套件 | none 原判 | none 宽判 | fast 原判 | fast 宽判 |
|---|---:|---:|---:|---:|
| Boundary，第 1 轮 | 0/18 | 5/18 | 1/18 | 7/18 |
| Boundary，第 2 轮 | 0/18 | 5/18 | 1/18 | 7/18 |
| Workbank，第 1 轮 | 3/40 | 4/40 | 1/40 | 2/40 |
| Workbank，第 2 轮 | 3/40 | 4/40 | 1/40 | 3/40 |
| BFCL product，1 轮 | 48/60 | 48/60 | 28/60 | 28/60 |

Boundary 的 B-V0 与 B-V1 在这些运行中相同：删除调用参数/禁用工具判据没有额外收益。
none 的 5 个新增通过为 csv_sum、json_extract、avoid_forbidden_tool、missing_file_recover、markdown_release_notes。
fast 原判通过 read_only_repo_explain；其宽判相对 none 新增 4 题、丢失 2 题，净 +2，不能只看净分。

Workbank 首轮 none 放宽后只新增 nt-0001，无需工具；36 道工具任务仍 0/36。
fast 放宽新增 fs-0001，答案正确描述最大文件 497 字节，但在重复调用后由 answer 阶段收尾。
这说明真实取证/内容能力有局部空间，仍不能称为自主闭环成功。
只删除 UNKNOWN：none 为 2/40（失去 nt-0003），fast 为 1/40（原答案是自然语言拒绝，不是 UNKNOWN）。
同时放宽答案并删除 UNKNOWN：none 为 3/40，fast 为 2/40。不能把这一混合改动的净分拿来衡量单一机制。

BFCL 分项：none→fast，不相关工具 11/20→1/20，缺参澄清 10/10→1/10，
参数齐全 8/10→10/10，多轮状态 9/10→6/10，错误恢复 10/10→10/10。
原判共新增 3 题、失去 23 题。后续逐题复核确认：fast 在不相关工具子集明显增加实际调用；
缺参子集的 9 道失分则仅因英文澄清没命中中文“路径/关键词”，不能据此声称澄清行为退步。
原判分数保留；行为与语言关键词匹配需分开解释，详见文末复核。

锚点 `pb_find_read_submit`：none 输出“说明文字 + 工具调用”，被解析成 final 并触发答案契约修复；
fast 能执行第一次 list_files，却重复调用后失败。两者都没通过，但并非同一种失败。
同模型不同开口已能移动失效阶段，这正是只看跨模型/跨 harness 的一个 pass/fail 无法定位根因的例子。

none 两轮 Boundary/Workbank 的严格和宽判通过名单均一致；原始终答分别有 17/18、38/40 逐字一致，
所以不能将 greedy 配置等同服务完全确定性。fast 两轮 Workbank 严格通过名单不变，
宽判第二轮新增 web-0001（自然语言回答默认 batch_size 为 512）；这是内容层面的一题波动。

## 16 题梯度、目录与 TERM 实测

以下四组使用同一修复前 binary，每组 16 题各跑一次。宽判为原建议的大小写敏感 contains，
不把终答中的文字一律判成协议错误。

| 配置 | 严格答案 | contains 宽判 | 宽判且在 ref_calls+1 步内自主结束 |
|---|---:|---:|---:|
| none，默认目录 | 0/16 | 9/16 | 2/16 |
| none，work-v1 | 0/16 | 12/16 | 6/16 |
| fast，默认目录 | 0/16 | 10/16 | 2/16 |
| fast，work-v1 | 2/16 | 4/16 | 4/16 |

| 格子（每格 2 题） | none 默认 | none work-v1 | fast 默认 | fast work-v1 |
|---|---:|---:|---:|---:|
| P0A0，给路径，复述整文件 | 2 | 2 | 2 | 2 |
| P0A1，给路径，抽字段 | 0 | 2 | 0 | 2 |
| P0A2，给路径，单文件求和 | 2 | 2 | 1 | 0 |
| P0A3，给两条路径，比较 | 1 | 2 | 1 | 0 |
| P1A1，README 指路 | 2 | 2 | 1 | 0 |
| P2A1，目录唯一候选 | 0 | 2 | 1 | 0 |
| P3A1，目录五个候选 | 2 | 0 | 2 | 0 |
| P4A1，搜索定位 | 0 | 0 | 2 | 0 |

这些曲线并非统一单调梯度，更不能解释成一个稳定的“计算墙”或“路径墙”。
默认 none 的 P0A1 已通过 read_file 得到正确字段，却又 search，遇到下述工具错误后放弃；
P3A1 反而能直接使用证据。work-v1 的 fast 在 P1A1 读到 README 路径后提前结束，
P2/P3/P4 多见裸 JSON、错误调用封装或截断，不是单纯的数值推理难度。

按 Claude 的目录假说，4 个实际工具变 12 个应该拖累锚点；实际 P0A1 在 none/fast 都是 **0/2→2/2**。
全体分数方向又随 thinking 改变，说明需要研究目录组成与 wire 的交互，而不是宣布“工具多所以不会做”。
默认目录的部分题还受到下述真实工具错误影响；不能将整张表当作纯粹目录数量的因果效应。

contains 也没有完全剥离格式：`west is larger` 不包含 `WEST`；`LARCH-684.` 等仍可匹配，
但不同大小写的标签或路径可能继续失分。新增**单独的** casefold 敏感性臂后，四组为 10/12/12/6。
casefold 也可能仅命中解释里的文件名，仍不是自动语义判分；主表继续使用事先定义的 contains，未追分改标准。

TERM 确实补充了信息：none/work-v1 的宽判 12 题中只有 6 题满足紧预算自主收尾。
但 fast/work-v1 的 4 个宽判全部及时结束，不代表更强，它同时损失了多数需要行动的题。
因此应并列报告“正确率 + 证据 + 终止”，不能让少行动掩盖失败。

## 额外发现：单文件 search_text 达到上限时误报错误

这不是 Claude 事先定位到的问题，而是新梯度轨迹提供的实际可复现故障。
`internal/agent/tools.go` 的 visitor 达到 max_results 后返回 `fs.SkipAll`。
目录分支用 WalkDir，会正常吞掉此停止信号；单文件分支直接调用 visitor，信号却泄漏成工具错误。
结果同时包含正确 matches 和 `ok:false/error:"skip everything and stop the walk"`，会诱发模型放弃。

最小回归测试 `TestSearchTextResultLimitIsNotAnError` 在修复前对单文件失败、目录通过；
修复为仅在单文件分支消耗 SkipAll，保持 matches/truncated、真正的取消错误不变。
修复后 `go test ./internal/agent ./internal/agent/eval ./internal/agent/wire` 全部通过。

主矩阵中 none/default 梯度 4 题、fast/default 梯度 6 题触发此错误；
原 Boundary/Workbank/BFCL 主矩阵没有该错误。不能拿它解释原 Workbank 的 3/40。
修复前 binary 保留，新 binary 为 `build/rwkv-cli-scorer-ablation-searchfix`；补跑结果单独记载，不覆盖旧分数。

| 默认目录补跑 | 原判修复前→后 | contains 修复前→后 | 新通过 | 新失败 |
|---|---:|---:|---|---|
| none | 0→0 /16 | 9→13 /16 | ladder-03、04、11、12 | 无 |
| fast | 0→0 /16 | 10→13 /16 | ladder-03、04、11 | 无 |

修复后均无 SkipAll 工具错误，单独 casefold 臂分别为 14/16、15/16，TERM 仍均 2/16。
原受影响的 10 条轨迹中，9 条在第一次错误搜索之前（含该次模型调用）模型输出与参数完全一致；
none/ladder-11 存在前段输出差异，保留该限制，不假称所有回放逐字相同。
本地确定性红绿测试与轨迹相同前缀共同支持工具回执修复带来内容收益。
严格格式仍全失败，说明这项真实修复与格式能力是两个问题；也没有在修复后重报原 40 题分数。

修复后 none/default 的阶梯更清楚：P0A0/A1/A2、P1A1/P2A1/P3A1 全部 2/2；
P0A3 为 1/2（另一题仅大小写，casefold 后 2/2）；P4A1 仍 0/2，失败在工具调用 JSON/think 协议阶段。
因此 **L 形诊断实验本身确实有价值**：它帮助排除了一个工具实现故障，并缩小了后续检查范围。
要反对的是“凭少量格子和跨套件总分就直接断言模型能力墙”的解释，而不是否定这类对照实验。

## 实验有效性、交付与建议

共 14 组主运行（416 次 case 执行）加 2 组 searchfix 补跑（32 次），合计 **448 次 case 执行**。
16 组均无已识别的 API 传输错误；此处不把工具执行或协议错误归为传输错误。
主矩阵的固定 raw 探针在 fast-r1 开始前与四组原梯度结束后，两条输出均逐字一致；
这不覆盖更早的 none-r1 或更晚的 searchfix 补跑，也不是服务端权重字节证明。
首轮全部 118 个 case 的首步 prompt，none/fast 仅空 think 开口不同，冻结题目与采样一致。

验证：Go agent/eval/wire 测试通过；重判器 5 个测试覆盖数字边界、句末标点、
执行/协议错误保留、调用判据独立消融与 casefold 独立性；所有归档原判通过状态均成功重构。
原评分器、冻结 40 题和 wire 默认值未更改。唯一运行时代码修改为 tools.go 的 5 行 SkipAll 处理，
配有 35 行回归测试。凭据仅通过私有临时文件/环境使用，不写入报告、manifest 或命令参数。

可复现工具：

- `scorer_ablation.py RUN... --out RESULT.json`：同轨迹配对重判。
- `make_diagnostic_ladder.py --out DIRECTORY`：生成 16 题诊断 JSON。
- `run_diagnostic_matrix.py --credentials PRIVATE.json`：执行 fast 主组、两轮复测与目录矩阵；
  需先用 `scripts/wire-experiment.py none-r1 --root runs/scorer-ablation-20260919 --binary build/rwkv-cli-scorer-ablation --buffered --parallelism 40 --suites boundary,workbank,bfcl --credentials PRIVATE.json`
  生成 none-r1 基线，并按本报告保留未修复/修复后两个 binary。脚本拒绝覆盖已有 run。
- `summarize_diagnostic_matrix.py --root runs/scorer-ablation-20260919`：汇总评分、取证、终止、逐题轨迹。
- `claude-diagnostic-results-20260919.json`：可进入 Git 的精简结果，含全部 448 次 case 的关键指标、
  翻转列表、模型/wire/binary/源文件摘要；原始完整请求和回执保留在 runs 目录。

结论与下一步：

1. **判据消融有效，但不能替“主要只是格式问题”背书。** Boundary 的部分失败确属格式；
   原 Workbank 的 36 道工具任务，在 none 两轮里即使放宽也仍全失败。继续保留端到端主分，增加内容/格式分项。
2. **补简单题是有实证价值的。** 这 16 题显示 9–13/16 的宽判区间，还抓到了原 40 题没触发的真实工具缺陷；
   因而“先不要补任何题”的强结论不成立。严格全零也说明只加题而不分开指标仍会遮蔽信息。
3. **不按当前 16 题直接宣称确定难度梯度。** 每格只有两题，模板/措辞相关；
   有大小写残留、工具错误、协议错误和过早/过晚终止。应先将这些格子变成独立题族，
   增加新的字段结构、文件名、语言和工具结果形态，在故障边界附近扩样，再校准 tier。
4. **目录和 TERM 对照值得保留，但解释需克制。** C 是组成×wire 交互，不是纯工具数量效应；
   TERM 从现有轨迹计算即可，不必复制“新题”，也不能奖励不会行动的模型。
5. **三位数可以是后续正式题库目标，当前证据不能定死 60/200/400。**
   先完成独立题族与评分契约，保留现有 40 题的冻结基线，再根据关注的回归幅度与族内相关性定样本量。
   本轮未实施拆仓库或训练数据生成；推断训练/MiSS 效果也不在本次 API 实验的证据范围内。

## 后续复核：no-call 行为与 App 默认

收到 Claude 对本报告的回复后，仅检查现有源码和已存轨迹，没有为本节调用新的推理 API。
此前正文及对话把缺参子集的评分下降简称为“澄清退步”，解释过强，现明确修正。

| 子集 | none 原判通过 | fast 原判通过 | none 实际调用真实工具 | fast 实际调用真实工具 |
|---|---:|---:|---:|---:|
| irrelevance 20 题 | 11 | 1 | 2 | 18 |
| missing 10 题 | 10 | 1 | 0 | 0 |
| 合计 30 题 | 21 | 2 | 2 | 18 |

这里实际调用指至少一条 action_type=tool、tool_executed=true 且不是 no_tool 的步骤。
fast 的 9 道 missing 失败没有工具调用，全部有明确英文澄清请求，唯一失败字段为
`output does not contain "路径"` 或 `output does not contain "关键词"`。
例如：`Please provide the full path to the file.`。中文题面引出英文回复可另计语言遵循，
但不能等价为“乱调工具”或“不懂澄清”。

因此 28/30 是原判失败率，**不是工具误调用率**。本次选定样本里实际调用率为 18/30，
其中 irrelevance 是 18/20，missing 是 0/10；不能把任一数字外推成 App 所有日常问题的概率。
none 的 7 道 irrelevance 失败也没有实际工具调用，包含协议失败/修复等情况。

当前源码的新建配置默认是 XML + thinking off：
`cmd/rwkv-app/frontend/src/state/providerManager.ts` 初始化 off，缺省恢复也为 off；
`api/service.go` 的 normalizeConfig 同样把空 Thinking 归一为 off。
这不能证明用户已保存或正在运行的配置也为 off，但否定“当前 App 代码默认 fast”的断言。
App 的 XMLHarnessOptions 路径也不能仅凭 fast 名字，等同本报告的
`bare+one-stage+no-tool+history=think-fast+thinkcontrol=off` 实验组合。

下一轮规模/链长设计需避免新的混杂：240 字节诊断 fixture 大量由换行补齐，
不是 240 字节有效任务信息；增加数据行会同时增加信息量与求和负担；拆文件加干扰又同时改变多个因素。
本轮 P0A2 实际是 list_files→read_file→search_text→no_tool，即 3 次真实工具调用、4 次生成，
“1 次调用”只是参考最短解。36 道工具题的 ref_calls 均值是 4.0，fixture 字节中位数 1349，
范围 0–8011（0 可为纯 web fixture）；tab-0001 的 1156 字节不是整个 Workbank 的代表性常量。

若继续实验，应分别控制：相同运算增加已读取上下文、相同上下文长度增加运算项、
相同数据改变文件分布、相同 fixture 隐去直接路径；干扰项再单独添加。
测到局部断点后，还须回到原题做去除/恢复该因素的配对干预，才能解释原 0/36 的一部分。


## 2026-09-20 后续预算与测量审计

后续对原 36 道工具题完成 max_steps 10→30 配对：官方 0/36→0/36，无新增通过；新 10 步运行出现 cfg-0001 的内容正确、格式失败，宽判为 1/36，30 步为 0/36。本文此前的“工具题宽判 0/36”只描述对应历史运行，不是模型不变属性。历史 ledger 的 max_turns_hit 还混入了重复调用收尾，G1K 的 21 中仅 3 是 step budget。完整结果、三条相同前缀长轨迹、token、语言判据静态审计见 [后续报告](budget-language-audit-20260920.md)。
