# G1K 失败诊断与能力释放实验（2026-09-18）

研究开始于 9 月 18 日，后续在线对照运行至 9 月 19 日凌晨；产物统一保留在 wire-check-20260918 目录。

## 结论范围

使用用户指定的全精度 G1K 远端服务，开展不涉及训练的推理与协议实验。本文区分正式任务通过、协议有效、答案内容、条件性能力诊断。

已有证据支持：当前工具循环确实损失了部分本来能完成的能力，但并不能据此断言模型已有高水平多步任务能力，只是被 Harness 隐藏。来源选择、工具语义、证据聚合、格式输出、协议和服务稳定性同时存在问题。

最后一组原始任务对照已经完成：同为非流式、并发 4，默认预算与实际 2048 预算均为 **3/40**，没有通过题翻转、没有网络错误，耗时 621→1231 秒。扩大预算对条件性答题有帮助，但单独用于当前 Agent 没有形成端到端收益。

逐题核对见 [40 题证据索引](failure-case-index-20260918.md)：包括动作顺序、强制收尾原因、原始验收错误、最终答案摘录及只读证据探针的对应结果。

## 1. 可重复的机械读数

主诊断源：`runs/wire-check-20260918/a0-backup-workbank/summary.json`。

| 现象 | 数量 | 解释边界 |
|---|---:|---|
| 正式通过 | 3/40 | 仅 nt-0002、nt-0003、nt-0004；其余 36 个工具任务均未通过 |
| 纯本地题首步误选 web 工具 | 7/28 | 按 first_step_metrics 的机械定义，包括能从 raw 识别的调用意图 |
| web 四题首步选 web 工具 | 0/4 | 来源方向双向错误，不是只需要禁止 web |
| 首步来源机械正确 | 23/40 | 只区分来源类别，不保证参数、路径、查询语义正确 |
| 重复触发强制收尾 | 21/40 | 重复是上游行为，强制转换是下游放大因素 |
| 步数预算触发收尾 | 3/40 | 与上项合计 24；其中有触发后没进入 answer 的情况 |
| answer 阶段仍发工具调用 | 18/40 | 共 34 个已解析真实调用；此时 Harness 禁止工具动作 |
| 最终空输出 | 22/40 | 多数被运行错误终止，不等于模型没有生成内容 |
| 成功读取过文件 | 12/40 | 读过文件不等于证据充分，也不等于正确理解 |
| 有真实工具尝试的回合 | 26 | wire_metrics 的分母，和成功取得证据不是同一概念 |
| 上述回合自主收尾 | 0/26 | 不是只看有没有输出 no_tool，必须区分强制 answer 阶段 |
| 工具回执完整出现在下一步 prompt | 120/120 | JSON 反序列化后比对回执；排除普遍的客户端漏传，不能证明模型利用了信息 |

生成上述机械诊断：

```sh
python3 bench/workbank/tools/failure_audit.py runs/wire-check-20260918/a0-backup-workbank
python3 bench/workbank/tools/first_step_metrics.py runs/wire-check-20260918/a0-backup-workbank
```

详细结果：`runs/wire-check-20260918/workbank-failure-audit.json`。下面的失败机制有重叠，不应把计数相加当成互斥错误桶。`work-v1` 的 web_search/web_fetch 使用固定 fixture provider，空搜索结果不是缺少 Brave/Tavily API key；用 G1K 和 DeepSeek 两个推理服务即可复现实验。

## 2. 代表性失败链

| Case | 真实行为 | 可以支持的判断 |
|---|---|---|
| cfg-0001、cfg-0002 | 本地服务配置问题先 web_search；返回空列表后反复相同搜索；dup 后切 answer，仍生成搜索调用 | 首先是信息源选择错误，其次是无法根据空结果换路线，最后是收尾阶段冲突。只恢复 parser 不会找到配置 |
| code-0001 | 生成文本表达要查 workspace 中的函数，却实际选择 web_search | 有任务理解片段，但行动选择没有落实；不能把可读的思考文本当作能力完成证据 |
| code-0004、log-0003 | 把 `TODO FIXME` 或完整自然语言查询传给字面子串 search_text | 把本地 literal search 当成语义检索；工具 schema 和示例可能比加宽解析更重要 |
| fs-0001 | 首次 list_files 已列出最大文件 497 bytes；继续读两个 CSV、重复读，然后 answer-stage violation | 很强的证据利用/停止控制问题；已用相同已获证据另开上下文答对 497，见能力探针 |
| doc-0001 | 找到会议纪要，正确复述三条 action items，但没有 write_file；最后称文件已创建 | 内容理解与执行完成脱节。不能因为最终回复内容正确就给文件任务加分 |
| doc-0003 | 查完政策后正确表达“没有相关政策”，但未按题目要求返回 UNKNOWN | 格式/出口问题是真实因素；与 fs、log、tab 的内容错误不能混为一类 |
| log-0001 | read_file 与 search_text 回执均含日期，最后却称“没有日期无法判断” | 证据已经进入 prompt，模型未正确利用；不是缺少文件内容 |
| tab-0003 | 已读完整月度 CSV，却逐日期调用 data_query，预算到期还在查下一天 | 规划粒度错误。单次 count 可解决的问题变成日期枚举，不是单纯多给一步就稳妥 |
| scr-0001、scr-0003 | 已读源码，接下来生成的修改调用形状错误 | 工具输出序列化/动作 schema 是执行瓶颈之一；恢复缺引号会改变代码内容，不能盲修 |
| nt-0001 | 输出 `9000 MiB per hour`，数值正确，但 plain-number judge 拒绝单位 | 是格式契约，不是单位换算能力错误。只影响这一个具体 case，不能替其余失败开脱 |
| code-0002 | 日志逐项只有 1 FAILED，尾部伪 summary 写 2 failed；G1K 和 DeepSeek 都取了尾部 | 有意设置的证据冲突题。当前题面已明确列出所有执行测试；不是普通的无陷阱“数一数” |

`nt-0001/NOTES.md` 前半仍保留旧版 MiB→MB 的解释，末尾才注明改成 MiB→MiB；当前判据必须使用 case.json 的 9000，不能使用旧说明的 9437.184。

本轮 DeepSeek native 参照为 **27/40**，与同事文档历史 30/40 分开记账。两者共同失败的题有 cfg-0003/4、code-0002/4、fs-0001、hyb-0004、nt-0001、scr-0003/4、web-0002。DeepSeek 也把 cfg-0003 答成 yes、把 code-0002 的错误摘要当成真实计数；另外 nt-0002/3/4 因不必要的工具调用等失败，恰好是 G1K 原始通过的三题。它不是金标或能力上界，native 通道、协议重试等也不同于 G1K text 通道，不能把 27−3 全部归因于模型参数能力或单一 wire 因素。

## 3. Boundary 暴露的潜力与边界

基线 0/18 中至少五个最终答案包含正确目标值：pb_csv_sum（42）、pb_json_extract（TCK-204）、pb_avoid_forbidden_tool（MANGO）、pb_missing_file_recover（COBALT-7）、pb_markdown_release_notes（--enable-v2-auth）。这不等于五题正式通过：必须继续检查工具限制、运行错误和 exact-output 契约。

`recovery=preamble` 后，BLUEBIRD、EMBER-91、47.80 等更多正确值到达了最终回复，但大量输出仍是叙述句，正式分数保持 0/18。`exit=final_answer` 那次的五个新增正式通过是：

- pb_json_extract
- pb_avoid_forbidden_tool
- pb_missing_file_recover
- pb_prompt_injection_in_file
- pb_markdown_release_notes

这解释了出口名称/字段可能有效的机制：让模型把最终 answer 写成目标值，而不是在 reason 里解释为什么可以结束。但它没有证明解决了多步计算：preamble run 的 fx、JSONL 聚合、CSV 对账仍出现真实数值错误，不能靠剥掉前后说明得到正确答案。

注意 `exit=final_answer` 同时更换工具名、字段和工具描述，是一个出口设计变体，不是“只改名字”的因果检验。这些历史变体也没有建立同事要求的完整 P0 新基线，不能宣称已经执行完其 W 矩阵。

## 4. 先前 BFCL 降分不能直接归因于 parser

对基线与 preamble 实验按 case/turn/step 对齐，完整 request 相同而输出不同的次数：

| 套件 | 对齐位置上相同 request | 其中 raw 输出不同 |
|---|---:|---:|
| Workbank | 156 | 14 |
| Boundary | 32 | 1 |
| BFCL product | 133 | 19 |

这些是描述性计数，不是独立同分布的随机重复样本，也不覆盖轨迹分叉后不再相同的请求。

`bfcl_recovery_multi_turn_base_0` 的前三个请求完全一致，前两步输出一致，第三步基线正常输出 BUDGET-READY，preamble run 却输出数百个 `The`。在这个分叉点前没有 preamble 恢复。因此，不能说这题由解析器宽容性造成退化；也不能未经控制试验就断言原因一定是随机采样、服务 cache 或 state 串扰。

本轮原配置 Workbank 重跑仍是 3/40，首步请求 40/40 相同，但首步输出只有 32/40 逐字相同。top_k=1 不足以作为当前服务端完全可重复的证明。

额外对 `bfcl_recovery_multi_turn_base_0` 的第三步做三次串行 raw 请求复放（非流式、相同 greedy 参数、服务端 EOS [0]）：三次 HTTP 200，原始输出逐字一致，均为正常 no_tool/BUDGET-READY 帧。没有执行生成的工具，也没有计入任务分数。证据：`bfcl-identical-request-serial-replay.json`；脚本 `scripts/wire-request-replay.py`。这没有定位最初差异的根因，只证明该固定上下文当前可稳定生成正常出口。

此外，此处 BFCL product 是仓库内 60 题产品化改编套件，包含路径已知读文件、缺参澄清和短状态任务，不是完整官方 BFCL 榜单分数；不能由 48/60 推导复杂工作区任务应该达到 80%。

## 5. API 与 token 预算核查

查阅并锁定上游 commit `b4f5a75565fa60657c948a24bad4573629eace99`：

- [HTTP API](https://github.com/Alic-Li/rwkv_lightning_cuda/blob/b4f5a75565fa60657c948a24bad4573629eace99/docs/http-api.md)
- [完整 API 文档](https://github.com/Alic-Li/rwkv_lightning_cuda/blob/b4f5a75565fa60657c948a24bad4573629eace99/rwkv_lightning_api_doc.md)
- [请求处理源码](https://github.com/Alic-Li/rwkv_lightning_cuda/blob/b4f5a75565fa60657c948a24bad4573629eace99/src/server/rwkv_api_service.cpp)

部署版本边界：9 月 19 日读取备用服务 `/v1/server/status`，其自报 `api_version=1.3`、`engine_version=albatross-1.3.0`。锁定的上游源码虽然 VERSION 为 1.7.0，但 `rwkv_api_service.cpp:1044–1045` 也硬编码返回这两个旧字符串，因此不能据此推断部署版本落后或不同。没有取得部署 commit，仍不能断言所有内部实现已与上游同步。本文以真实请求/响应验证接口行为，以锁定的源码解释可能机制；`think_type=free` 的具体 mask 实现属于上游源码事实，尚未在该部署上做独立行为验收。记录在 `server-version-audit.json`。

CUDA `/v1/batch/completions` 接收 contents；stop_tokens 是整数 ID 数组。手工探针使用字符串 stop_tokens 返回 500；同一探针改成 [0] 返回 200。但项目 CLI 的 provider 已经正确选择 EOS，故此手工探针错误不能解释之前的正式模型分数。没有据此修改已有正确的 provider。

CUDA chat/messages 路径会应用服务端 think 模板，batch/contents 路径保留 raw prompt。直接把请求改成 chat/messages 会同时改变模板，不是等价替换。

上游 `think_type=free` 除了预填 `<think`，还会在第二、第三个生成 token 对 111/754 做 reasoning mask；项目 `thinking=full` 只控制自身模板，并不等价于启用该服务端 mask。服务端文档的通用采样默认值还包含 presence=2.0、frequency=0.2、decay=0.996、top_k=20、top_p=0.3，而本组实验固定 greedy、零惩罚。两者是待做的受控校准变量，不能直接把官方聊天请求与 Agent 分数横向比较，也不能由一次微弱 penalty 无效推导所有惩罚设置都无效。

上游明确说明 SSE 固定返回 finish_reason=stop，无法区分自然结束、token 上限、管理中断。模型 trace 的 0 usage 也不是实际没生成 token。使用项目 RWKV 词表重分词：

- Workbank log-0001 首步正好 512 tokens，上限 512，却标 stop，报未闭合 think。
- Workbank log-0002 answer 第 6 步正好 1024，上限 1024，却标 stop，报 JSON EOF。
- BFCL 基线六次输出恰好达到 512，仍标 stop；包括 irrelevance_7/11/18/21/28。

重分词是诊断信号，不等价于服务端原始 token 使用量。另对 `bfcl_irrelevance_0` 第一请求做了一次串行 raw 复放：HTTP 200，原始响应 2033 字符，旧 trace 为 446 字符，raw 的前 446 字符与旧 trace 逐字一致；在第一个 `</tool_call>` 处截断恰好复现旧 trace。该标签位于 think 中对协议示例的引用，因此这个样本确实被客户端提前截断，并非模型在此自然结束。

但完整 raw 重分词仍恰好 512 tokens，反复重复“25 square meters”，没有闭合 think、没有最终答案帧。故同一失败同时存在客户端截断和模型循环，不能声称取消文本 stop 就会让该题通过，更不能把 think 里的示例执行为真实调用。证据在 `think-stop-raw-replay.json`；未执行生成的工具，未重记正式得分。

上下文大小也已量化：Workbank 182 次生成的输入 token 中位数 1448，最大 4335，只有 2 次超过 4096；40 个首步为 992–1104 tokens。BFCL 155 次输入中位数 553、最大 1057。没有证据把这些失败统一解释成极长上下文溢出；模型能否有效利用其中的信息仍是另一回事。

## 6. 条件性能力探针

已生成两组 32 个只读问答诊断，排除八个需要实际文件修改的 case：

1. observed：仅重排该模型原轨迹中成功工具回执，不提供新文件或金标。
2. oracle：提供所有 fixture 文件及网页正文，包括干扰文档，并注明文件字节大小和行号；不按金标挑选证据。

两组均保留原答案判据，并要求零工具调用。它们改变了信息可得性、上下文形式与任务指令，**不是原始 Workbank 成绩，也不是可直接部署的提分方案**。oracle 不是严格数学意义的能力上界，因为把所有文件一起提供也会增加干扰。

生成器：`bench/workbank/tools/evidence_probe_cases.py`。

observed 第一轮含七个网络失败，整个 run 不进入正式能力分数对比。完整返回的单题可用于定性诊断：fs-0001 得到 497；doc-0003 得到 UNKNOWN；code-0003 得到 7（应为 3）、log-0001 得到 5（应为 6）、tab-0003 得到 15（应为 19）。

oracle 串行、非流式第一轮完整结束，无基础设施错误：**8/32**。通过为 cfg-0001、cfg-0002、code-0002、fs-0001、hyb-0001、nt-0002、web-0001、web-0003。其中七个是原始基线失败的工具类只读题，说明信息获取过程确实损失了可完成的部分任务；nt-0003/4 反而退化，说明信息/提示越多并不必然更好。

该轮首步预算仍为 512，十个 case 最终报未闭合 think，不能据此宣称“给齐证据也只会 25%”。条件性任务要求不调用工具，因此也不测量模型借助 calculator/data_query 可以达到的上限。

第二轮只指定 `--decision-max-tokens 2048`，发现真实请求仍为 **1024**，被全局 `--max-tokens` 默认值截断（`internal/agent/runner.go:153`）。所以保留 `evidence-oracle-2048-serial-workbank` 原目录名，但分析按**实际 1024**统计。结果 **10/32**、无基础设施错误：新增 nt-0004、tab-0002，无通过转失败；tab-0004 已有正确数值但带说明而失败，tab-0001 的数值仍错误。第三轮同时显式设置两个上限到 2048，并以 trace 的真实 request budget 为准。

第三轮 `evidence-oracle-effective2048-serial-workbank`：42 次实际生成请求预算全部为 **2048**，无基础设施错误，正式诊断判据 **12/32**。对 1024 轮：新增 fs-0004、log-0001、log-0003，失去 nt-0004；对 512 轮：新增 fs-0004、log-0001、log-0003、tab-0002，没有通过转失败。未闭合 think 导致的最终运行失败从 10→7→4 个 case。

| 诊断条件 | case 通过 | 最终未闭合 think 失败 | 有网络错误 |
|---|---:|---:|---|
| 全部原始证据，首步 512 | 8/32 | 10 | 否 |
| 同证据，实际 1024 | 10/32 | 7 | 否 |
| 同证据，实际 2048 | 12/32 | 4 | 否 |

直接核对原始生成前缀：fs-0004、log-0001、tab-0002 在 2048 轮的第一步输出，都完整保留了 512 轮的第一步输出作为逐字前缀，然后继续生成直到得到正确答案；第一步 prompt 也完全相同。这三题提供比单看两次分数更强的预算截断证据。log-0003 的前缀不完全相同，只报告观察到的翻转，不作同样强的因果归因。

2048 下仍有内容错误：cfg-0003=yes（应 no）、doc-0002=60 days（应 45）、tab-0001=5389.95（应 5548.95）、tab-0003=15（应 19）、log-0004=0（应 8）、web-0002=120（应 45）、web-0004=128（应 256）。另外 fs-0002、fs-0003、nt-0001、tab-0004 出现内容正确但严格输出格式未满足的情况。故不能把全部剩余失败归为协议或预算，也不能把 12/32 当成能力上限。

### 6.1 原始 40 题的实际提分验证

两轮使用原始 fixture 和判据、同一 binary、同一 profile、非流式传输、并发 4、max-steps=10，不启用 rescue。40/40 首步 prompt 完全一致，唯一配置改动为生成 token 预算。对照默认预算真实请求为 51 次 512、121 次 1024；实验轮 161 次请求全部为 2048。不同轨迹产生的请求总数不同。

| 指标 | 默认预算 | 实际 2048 |
|---|---:|---:|
| 原始 Workbank 通过 | 3/40 | 3/40 |
| 新增 / 失去通过 | — | 0 / 0 |
| 网络错误 | 0 | 0 |
| 自主收尾 / 有工具尝试回合 | 1/23 | 1/22 |
| 强制收尾触发 | 20 | 19 |
| dup 拒绝 | 17 | 16 |
| answer 阶段工具调用 | 28 次 / 15 题 | 24 次 / 13 题 |
| 最终空输出 | 19/40 | 19/40 |
| 成功读取过文件 | 12/40 | 12/40 |
| 首步来源机械正确 | 23/40 | 24/40 |
| 整组耗时 | 621 秒 | 1231 秒 |

这组对照不支持单独增大预算作为已验证的提分方案：通过仍是 nt-0002/3/4，行为指标仅轻微变化，耗时约翻倍。非流式路径在拿到完整响应后才按客户端文本 stop 截断，因此增加预算可能带来不可见于已截断 trace 的额外生成；耗时差不能精确等同于 token 成本差。本组没有扩展到 Boundary/BFCL，不能声称完成三套件预算护栏验收。完整对照见 `practical-budget-comparison.json`。

## 7. 优先实验与采用标准

1. **服务复现性**：固定 prompt 哈希、token/sampling 参数和请求形式，串行重复与固定 batch 重复，保留原始 response。无法稳定复现前，不把一次涨跌归因为改动。
2. **think 与停止条件**：区分 EOS、客户端文本 stop、预算触顶；测试每步思考时同步移除禁止 think 的 nudge，再单独扩预算。禁止把多个轴的收益分配给其中一个轴。当前 full-thinking 尝试受断流影响，未形成有效整组结论。
3. **答案出口**：preamble 与 final_answer 分开测试后再测组合；Boundary 是最有根据的正向候选。正式分数、无工具任务护栏、工具预算和误调用率一起验收。
4. **来源与工具理解**：相对路径快照、字面搜索的正反例、空结果后换路线；不以“所有题先 list_files”替模型做决定，避免伤害 web/no-tool 任务。
5. **工具结果到行动**：已获证据另上下文可答对，才优先试 generic evidence-only answer stage；它属于 Harness 辅助收益，不能记作自主停止能力。
6. **计算与聚合**：data_query 正确的 count/filter/group_by 示例、日志过滤计数工具、写文件后验收。若 oracle 仍失败，继续调出口不能解决主要问题。

不会修改已有 case 的 expected 值、训练评测题、默默剥掉答案单位重记正式分数，或把 HTTP 失败计入模型失败。

## 8. 本轮有效性记录

- 原 `a0-backup-*`、`recovery-preamble-*`、`exit-final-answer-*` 保留原始分数与轨迹。
- `cuda-eos-baseline-workbank`：有效，3/40；其 boundary 有 6 个断流错误，排除；BFCL 未继续。
- `thinking-full-workbank`：40 个 EOF，排除；boundary 18 个 TLS 超时，排除。
- `cuda-eos-think-policy-workbank`：20 个 EOF，排除，不将表面 2/40 记为模型成绩。
- `evidence-observed-workbank`：7 个网络 EOF，排除整组比较；完整单题仅作定性观察。
- `evidence-oracle-serial-workbank`：有效的条件性诊断，8/32；不是 Workbank 提分。
- `evidence-oracle-2048-serial-workbank`：有效的条件性诊断，10/32；实际预算 1024，名称不能代替 trace 配置。
- `evidence-oracle-effective2048-serial-workbank`：有效的条件性诊断，12/32；实际预算 2048。
- `practical-buffered4-baseline-workbank`：原始 40 题、非流式、并发 4 的匹配基线，有效，3/40，621 秒，无基础设施错误。与 a0 的通过题相同；dup 拒绝 17、强制触发 20、自主收尾 1/23、answer 阶段工具调用 28 次（15 个 case）。行为计数有变化，但没有任务收益。
- `practical-buffered4-budget2048-workbank`：原始 40 题预算对照，有效，3/40，1231 秒，无基础设施错误；全 161 次请求实际为 2048，零通过翻转。
- `wire_metrics.py` 更新到 wire-audit-v2，统一识别 provider/transport failure，区分它与模型生成 JSON 的 unexpected EOF。

本轮运行已收尾，产物保留在同目录。没有变更产品默认 wire、没有提交或推送。

## 9. 对同事实验清单的具体判断

- **接受其问题方向，但不直接接受因果桶数量**：开场白后调用、自主收尾困难、后续重复和严格输出不匹配都可在新轨迹中观察到。“开场白中存在调用”不是“放宽 parser 后任务就会通过”的同义词；完整任务仍可能因来源错误、参数错误或答案错误失败。
- **P0-1 中的任意位置提取需要收窄**：think 内可能是在复述协议或举例，不能仅凭出现 `<tool_call>` 就执行。审计脚本现在分别记“提及调用”和“完整调用候选”，不把它们直接算成可抢救的成功任务。已测 preamble 变体也没有实现“所有未闭合 think 任意提取”的策略。
- **P0-2 的缺引号修复不是纯测量修复**：补引号可能改变路径、代码或文本参数含义；本轮实验只允许完整 JSON 后多余闭括号的窄修复，不猜缺失内容。
- **W3 有真实依据，但 256-token 强制闭合尚无实证**：已观察到模型沿相同输出前缀继续推理后答对，不能把完整思考强行缩短到 256 当作等价修复。应独立验证预算、停止条件和强制闭合，而非一次全部改动再统一归因。
- **W1 是候选，不满足合并条件**：出口变体提高了 Boundary，但 BFCL 44/60，低于清单 ≥47/60 的护栏；Workbank 仍 3/40。不应据此定版 wire-v2。
- **不采纳“以后不必测 penalty”的外推**：一组温和惩罚无效，只排除那一组设置；但本轮也没有证据建议直接采用上游聊天默认采样。
- **S 训练线本轮不执行**：用户明确要求不训练。没有用评测题训练 state，没有把诊断探针视为训练收益，也没有宣称完整 P0→B0→W→C 矩阵已经验收。
