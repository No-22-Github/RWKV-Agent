# state-final.pth 在 workbank 的评测（2026-09-20）

**结论：这枚 state 没有修好 workbank，反而把通过数从 3/40 压到 1/40。** 它确实被正确加载、并且把输出形态拉到了训练分布上（信封、无 think、no_tool 收尾都出来了），代价是决策内容跑偏：首步动作从"经常不调工具"变成"几乎必调工具"，且首选 `web_search` 的比例是语料的 3.6 倍。同批对照里 BFCL product 47→49、Boundary 0→1，方向与 9-19 轮一致（state 对 BFCL 略有帮助，对 workbank 无益）——仍是能力重排，不是净提升。

分支 `main`，数据在 `runs/state-check-20260920/`（未提交，`runs/` 被 gitignore）。本轮没有训练，没有改判分器或历史 ledger。

## 运行身份与有效性

| 项 | 值 |
|---|---|
| 端点 | `https://api-7b.rwkvos.com/v1`，模型 `rwkv-g1k-7b-temp-3601` |
| state 文件 | `/Users/no22/Downloads/state-final.pth`，16,785,536 B，SHA-256 `0fd15447…be284` |
| 上传 | `rwkv-cli state upload` → `state_id=state-final.pth`，回执 `runs/state-check-20260920/state-final.pth.upload.json` |
| 二进制 | `build/rwkv-cli-state-experiment` SHA-256 `39ed9de8…`，git `afaeb79a` |
| wire | 六次 run 的 `run.json` `wire_hash` 全为 `6b5630aa…`，与 ws700 语料生成时的快照逐字符相同 |
| 用例 | `case_source_sha256 8928487db5f01c63…`（冻结的 40 题银行，未改动） |
| 有效性 | 6 个 run 全部 `canary_stable=true`、`state_registration_stable=true`、`infrastructure_errors=0` |
| 采样 | top_k=1 / temperature=1 / top_p=1、penalty 0/0/1、贪心单跑、40 case 并发、max-steps 10、rescue 关闭 |

两臂唯一差异是 `--state-id`。零 state 臂在**当前二进制**上复现了 9-19 基线：3/40，且通过题完全相同（nt-0002/0003/0004），所以这次对比不受 9-20 那次 `tools.go` 改动影响。

state 文件结构：32 张 `(64,64,64)`、`BFloat16Storage`（9-17 的两枚是 fp32）。服务端源码 `load_state_from_pth` 显式接受 `kBFloat16`/`kFloat32`，并按声明的 dtype 逐元素转换（`read_element_as_float` → 运行时 fp16），bf16 与 fp32 走同一条转置路径，不是被当成 fp32 误读。

## 对齐证据：state 确实生效且吃到了训练分布

语料：`outputs/workspace-agent-700-state-tune-textonly/train.textonly.jsonl`（630 行训练，来自 ws700 的 36 个锚点家族：每族 1 条锚点行 + 变体，另 70 行验证；全文本 dense loss）。四项独立检查：

1. **prompt 字节级一致**：40 题里 36 题能在语料中找到锚点行，这 36 题的评测首步 prompt 与锚点行的 prompt 前缀**逐字节相同**（36/36）。做法：取 `summary.json` 的 `cases[].turns[0].result.steps[0].request.prompt`（harness 实际发出的 prompt），与渲染语料文本截到第一个 `\nAssistant:` 的前缀比对；语料在该边界之后接 `" " + assistant 轮`，边界对齐即命中。可复跑：`python3 bench/workbank/tools/extract_anchors.py <out> --scope anchor`（脚本同时把这 36 行导成训练用 JSONL）。语料里没有 `nt-0001..0004` 的对应行。
2. **首决策探针**（新脚本 `scripts/state-corpus-probe.py`，24 条语料行，贪心续写）：零 state 首 16 字符复现率 0/24，state 臂 **24/24**；首个工具名与语料一致 1/24 → **11/24**。形态完全命中，决策部分命中。
3. **自发 think 消失**：`think_self` 37→1、`first_think` 33→0，与"训练文本 assistant 段不带 think 前缀"一致。
4. **收尾习俗迁移**：state 臂出现 `no_tool` 信封收尾（语料有 294 次 no_tool 调用），零 state 臂几乎不用。

补充：语料里 **0 处 WORKBANK-CANARY**，没有把评测题的 canary 打进训练文本；36/36 锚点的 `verification.replay_status=passed`、每锚点至少 2 次干净重放、`content_pass` 全为真，且锚点的期望值与 workbank 用例的 `expect` 一致（例：cfg-0001 的两边都是 8431）。

## 结果矩阵

| 套件 | 零 state（对照） | state-final | 差 |
|---|---:|---:|---:|
| workbank 40 | 3（nt-0002/3/4） | **1**（doc-0001） | −2 |
| boundary 18 | 0 | 1 | +1 |
| BFCL product 60 | 47 | 49 | +2 |

耗时：workbank 174s / 233s，boundary 69s / 162s，bfcl 103s / 82s。

## workbank 行为学：从"不调工具"变成"必调、且偏向网页"

首步动作分布对比（同一批 40 题）：

| 首步动作 | 训练语料 630 行 | 零 state | state-final |
|---|---:|---:|---:|
| `list_files` | 374（59%） | 6（15%） | 8（20%） |
| `web_search` | 91（14%） | 7（18%） | **21（53%）** |
| `read_file` | 68（11%） | 4（10%） | 4（10%） |
| `search_text` | 47（7%） | 5（13%） | 1（3%） |
| `calculator` | 0 | 0 | 2（5%） |
| 首步不调工具 | 0 | **17（43%）** | 3（8%） |

其它进程级指标（`wire_metrics` / `failure_audit`，零 state → state）：

- 工具构成：`web_search` 29→82、`web_fetch` 1→16，`read_file` 32→17、`search_text` 14→9——本地取证减少、网页检索增加。
- 复读与强制收尾：相邻重复 20→46、duplicate reject 19→27、forced closeout 22→34、answer 阶段工具调用 29→51。
- 空终答的题 20→**31**；成功读到文件的题 11→6；零工具调用题 16→3。
- 四道 no-tool 题（nt-*）零 state 过 3 道，state 臂**四道全调工具**：nt-0001/nt-0004 先 `calculator` 再 prose 收尾（数值其实算对：9000 / 720），nt-0002/nt-0003 连调三次相同 `web_search` 后散文作答。"want []" 判负 0→4。

单题机制样本：

- `log-0001`（新增失败）：`data_query` 用 `operation=count` 同时带 `field="count(*)"` → 工具报 `invalid tool arguments: count does not accept field or expression`，第 2、3 步原样重发（只改 filter）→ duplicate → 强制收尾 → answer 阶段继续复读同一调用 → 终答为空。**语料自身没有这个错法**：75 次 `data_query` 调用全部符合 harness 的聚合参数规则（30 次裸 `count`、18 次 `distinct_count`+field、22 次 `sum`+field 等），没有 `count` 带 field 的写法。所以这是模型自造参数组合且不按错误回执修复。
- `doc-0001`（新增通过）：`read_file → list_files → read_file → read_file → write_file(tasks/todo.md) → no_tool` 六步完成交付，是 state 臂唯一真实赢下的题，形态与语料一致。

## 解释与限制

可以说的：这枚 state 把**形态**装上了（信封、无 think、no_tool 收尾），把**倾向**改强了（几乎必调工具、偏向 web），但没有装上**按 prompt 条件化的决策**——在它训练过的同一 prompt 上，首步选择与语料锚点一致率只有 11/36（零 state 7/36），而语料锚点 61% 是 `list_files` 起步，state 却在 15 道本地题上首步 `web_search`。

不能断言、但值得下一步验证的两条训练侧假设：

1. **全文本 dense loss 稀释了动作监督**：转换报告记录监督 token 111,020 / 全文本 token 1,193,492（约 9% 落在 assistant 侧），梯度主体在建模上下文而不是动作策略。要不要给 `rwkv_state_tune` 补 loss mask，是可以设计对照的。
2. **锚点被同族变体稀释**：36 个锚点每个在 630 行里只出现 1 次，同族另有 17 行任务文本与夹具都不同的变体；同一 prompt 的目标轨迹没有配比优势。

限制：workbank 每臂只跑一次贪心（本仓库既有协议），40 并发下单题有抖动——不过零 state 臂与 9-19 基线逐题一致，说明聚合层面可复现；`plan`/`route` 等 stage 指标未另做分析。BFCL product 只是本仓库的 60 题产品子集，不是官方榜单。

## 补充分析：网页偏向的来源（不是数据偏向）

语料本身**不偏网页**：630 行训练数据的首步动作是 `list_files` 374（59%）、`web_search` 91（14%）、`read_file` 68、`search_text` 47；只按"本地类题"看，语料首步选网页的只有 1/32（3%），而 4 道网页题 4/4 选网页。整体工具构成里 web 系（web_search 136 + web_fetch 191）占 327/3073 ≈ 10.6%。

实测首步网页率（同一批题、同一个 prompt）：

| 分组 | 语料锚点 | 零 state | state-final |
|---|---:|---:|---:|
| 本地类题 n=32 | 1（3%） | 7（22%） | **16（50%）** |
| 网页类题 n=4 | 4（100%） | 0 | 3（75%） |

关键反证：在 36 个与训练锚点**逐字节相同**的 prompt 上，state 的首步与锚点一致率 11/36，**低于"永远选 list_files"这一常数基线 22/36**（零 state 7/36）。也就是说它没有装上"按 prompt 选择动作"的条件化策略，装上的只是表层形态。

机制（推断，非已证）：网页查询的论元可以直接从用户文本抄——`cfg-0001` 发的是 "notify-hub service TCP port load balancer"，`doc-0003` 发的是 "company pays back home internet bill expense policy"，都是题面改写；而 `list_files`/`read_file` 要求先决定"看哪个路径"，正是条件化知识没装上时最先塌掉的部分。基座先验本来就偏网页（零 state 本地题 22%，语料只有 3%），state 把这个先验进一步放大。旁证：全文本 dense loss 下 assistant 侧只占 111,020/1,193,492 ≈ 9% 的监督 token。

## 补充分析：两臂皆败的 36 题，轨迹往哪走了

阶梯口径（逐题取到达的最远处，自下而上）：0 无动作 → 1 有调用但全失败 → 2 只拿到网页证据 → 3 拿到本地证据 → 4 有终答但契约不合 → 5 通过。

转移矩阵（零 state → state，n=36）：前进 13、后退 10、持平 13。但前进几乎都在低阶——13 例里 11 例只是"从全部调用失败变成至少拿到网页证据"，只有 2 例真正产出终答；后退集中在丢本地证据：`code-0004`/`fs-0004`/`log-0002`/`log-0003`/`scr-0001`/`tab-0003`/`web-0004` 从"拿到本地证据"掉到只剩网页证据或全失败，`log-0001`/`doc-0003` 从"有终答"掉到没有终答。

聚合量（零 state → state）：

| 指标 | 零 state | state |
|---|---:|---:|
| 成功的工具调用 | 76 | 115 |
| 其中成功的**本地**取证调用 | 52 | **29** |
| 网页调用（其中失败） | 30（9） | 98（**21**） |
| 命中锚点轨迹里的决定性文件 | 7/31 | **4/31** |
| 失败题里有模型终答 / 空终答 | 11 / 26 | 6 / 33 |
| 失败题里**终答内容已含期望值** | 1 | **5** |

结论是两句话：**更积极、更持久是真的**（成功调用 76→115、零证据退出 12→2、零工具题 16→3），**更靠近正确答案不是整体成立**——到决定性证据的到达率下降、把证据转成终答的比例下降。唯一确实变好的是"内容层"：失败题里内容已到位的从 1 题升到 5 题（`fs-0002` 说对了 `config/history_retention.yaml`、`web-0001` 从 UNKNOWN 改成答对 512、`nt-0001/0002/0004` 数值也对），全部卡在答案契约（`output_equals`、plain number）或 `tools=[]` 上。

答案契约这一层不是语料教错：语料 294 次 `no_tool` 收尾里 91% 是纯值或短值（156 纯数字 + 112 短值），散文只有 26 次。state 却把答案写成解释性句子——和"网页偏向"同一个病根：表层形态装上了，条件化的策略与纪律没装上。这也是 `nt-0002` 从"443"（零 state 通过）变成 "HTTPS uses port 443 by default."（state 失败）的原因。


## 补充分析：多步段的对齐缺口（语料缺 harness 的 post-tool 提醒）

首步 prompt 逐字节相同（36/36）只覆盖第一次决策。评测从第二步起，harness 在每次工具回执后会追加一段 User 提醒：

- `internal/agent/protocol_g1.go` 的 `PostToolReminder()` → `Use the Tool results above to continue the current task. If the evidence is sufficient…Never repeat a successful tool call.`
- 重复调用被拒时换成 `duplicateToolAnswerReminder`（`That tool call was rejected because it repeats a successful call.`），协议出错另有修复提示。

而 ws700 渲染器 `tooling/workv1_wire.py` 只写 `\n\nUser: <tool_response>…</tool_response>`，**700 行语料里这三类提醒一条都没有**（逐串计数 0）。对照：真实 harness 轨迹 `runs/budget-language-audit-20260920/none-steps10` 的 129 个 step≥2 prompt 里 120 个带这段提醒；本轮 workbank 的 state 臂 191 个 step≥2 prompt 里 166 个带提醒、6 个是 duplicate 版、其余为修复提示，40 题中 39 题进入第二步、其中 28 题第二步 prompt 直接带提醒。

推论：**第一步在分布内，第二步起每一条评测 prompt 都不在语料分布内**（语料里根本不存在该字符串，所以任何含提醒的评测 prompt 都不可能是语料文本的前缀）。这解释了为什么"复现"只成立于首步，也把后续失败的一部分归到语料契约而非 state 容量：多步段的转写形态、收尾提醒、重复拒绝提示都没有进过训练。

对"把步骤焊死去"的实验，直接影响是：先补渲染器（把 post-tool / duplicate / 修复提示按 harness 的拼接方式写进语料）再重渲，否则焊得再狠，训练分布与推理分布仍差一整段 User 消息。

## 验证性实验：把 post-tool 提醒去掉（`--wire nudge=none`）

猜想是"语料没有 harness 的提醒，所以多步段 OOD；去掉提醒，state 应当变好"。实测结果：提醒确实去掉了，**但没有任何超出噪声的变化**。

配置：`--wire nudge=none` → `G1Protocol.PostToolReminder()` 返回空串。wire 规范串新增 `;nudge=none`，`wire_hash` 由 `6b5630aa…` 变为 `625533bb90d1ff33…`；四次 run 的首步 prompt 与语料仍 36/36 逐字节相同（System 控制句没动）。四次 run 的 canary 只有 `zero-nudge` 那次严格指纹不稳定（漂在客户端停止标记之后，effective-stable），其余三组严格稳定。

| 指标 | 零 state 默认 | 零 state nudge=none | state 默认 | state nudge=none |
|---|---:|---:|---:|---:|
| 通过 | 3 | **4** | 1 | **0** |
| 有终答 / 空终答 | 20 / 20 | 18 / 22 | 9 / 31 | 10 / 30 |
| 前 3 步重复≥3 的题 | 17 | 18 | 30 | 27 |
| 触发强制收尾的题 | 22 | 22 | 34 | 32 |
| answer 阶段仍调工具的题 | 16 | 19 | 28 | 27 |
| step≥2 步数 | 126 | 140 | 191 | 205 |
| 其中带 post-tool 提醒 | 116 | **0** | 166 | **0** |
| 与语料前缀一致 ≥2 步的题 | 0 | 2 | 0 | 1 |

三点读数：

1. **开关有效但不够**：post-tool 提醒 116→0、166→0，可 switch 能动的只有这一族。同一批次里 answer 阶段指令（39/53 步）、duplicate 提醒（36/44）、失败提醒（28/44）、修复提示（12/3）**依旧在**——它们没有 wire 开关，要完全变成语料那种转写形态得改代码加轴。
2. **纪律类指标原地不动**：重复≥3 的题 30→27、强制收尾 34→32、answer 阶段工具 28→27，方向一致但幅度在 n=40 单次贪心的噪声量级内；通过数反而是 1→0。去掉"够了就收尾、别重复调用"这句提醒，并没有把 state 的收尾病治回来。
3. **对齐深度几乎没变**：即便提醒归零，评测转写与语料"连续 ≥2 步逐字节一致"的题也只有 2 题（零 state）和 1 题（state）。原因是这个深度要求模型先精确复现首步的 (工具, 参数)（语料同参数才会产生同回执），而这一步本来就极少命中（默认 wire 下 state 1/36、零 state 2/36）。

唯一的清晰翻转是 `doc-0001`（多步交付题：读→列→读→写 `tasks/todo.md`→no_tool）：默认 wire 下 state 通过、零 state 失败；去掉提醒后变成零 state 通过、state 失败。提醒在这里充当"继续/收尾"的压力，两种策略对它的响应相反。

**结论：提醒缺口是真的（语料契约问题，值得单独修），但它不是这枚 state 在 workbank 失败的主因。**主因仍是决策策略本身（何时停、下一步调什么）没有被装上——去掉 OOD 段之后行为几乎不变，正好把这一点反证出来。继续做"焊死"实验时：首步是干净的分布内目标；多步段若要用无提醒的转写形态，应先补渲染器与 wire 轴，但按本实验结果，不要期待它单独带来通过数提升。

## 追加：state_out_A（37 行、270 步）——焊接的不是策略，是把 state 吹到了 3,500×

用户 2026-09-20 深夜提供 `state_out_A/`（37 行子集、270 步、loss 2.x→0.7，`state-final.pth` 与 `state-step-00000270.pth` 同文件，sha256 `c4f41259…`，与我先前评测的 `0fd15447…` 不同）。六个 checkpoint（45/90/135/180/225/270）全部上传并跑完 workbank S0 40 题：

| checkpoint | 通过 | 有终答 | 首步=list_files | 出现过的工具数 | 终答碎片复读的题 | canary 可读 | 指纹稳定 |
|---|---:|---:|---:|---:|---:|---|---|
| 零 state（对照） | 3 | 20 | 6 | 9 | 0 | 是 | 是 |
| 上一枚 state-final | 1 | 9 | 8 | 9 | 0 | 是 | 是 |
| outA-45 | 0 | 39 | 0 | **0** | 0 | **否** | 否 |
| outA-90 | 0 | 23 | 30 | 4 | 1 | 否 | 否 |
| outA-135 | 0 | 12 | 40 | 2 | 2 | 否 | 否 |
| outA-180 | 0 | 28 | 16 | 3 | 20 | 否 | 否 |
| outA-225 | 0 | 12 | 7 | 3 | 10 | 否 | 否 |
| outA-270 | 0 | 38 | 40 | 1 | 31 | 否 | 否 |

**根因（数值证据）**：用 `bench/workbank/tools/state_sanity.py` 直接解析 pth 的 bf16 张量——上一枚可用 state 的中位 RMS 为 **0.001059**（max|v| 0.0026），而 outA 六个 checkpoint 的中位 RMS 全在 **3.5–3.9**（max|v| 28–49.5），**放大倍数中位数 3,753×，且 32 层一致**（层间比值 2,825×–5,866×），无 NaN/Inf。也就是说这不是"过拟合到后期"，而是**优化尺度问题让 state 从一开始就落在崩溃区**：最早的 step-45 checkpoint 已经不可用（canary 是词沙拉、40 题里一次工具都没调）。

**行为证据**：焊接确实在"表面"生效——step-135/270 首步 40/40 命中 `list_files`（健康的零 state 只有 6/40）；但紧接着第二步就退化成英文碎片复读（例：`The tool calls the tool's inventory, in the tool calls. Reply with only the final answer. Reply with only the final answer. …`），工具词表从 9 个塌成 1–4 个，重复碎片的题从 0 涨到 31。loss 降到 0.7 与这种退化是自洽的——复读片段是最容易预测的序列，**loss 下降在这里是症状，不是学习**。

**结论与操作建议**：

1. 任何训练产物先过闸再花评测预算：`python3 bench/workbank/tools/state_sanity.py <new.pth> --reference <已知可用 state>`，退出码非 0 即闸门失败（本次六个 checkpoint 全部 FAIL，比值 3,473×–3,615×）。
2. 这一轮的差距在**优化尺度**（32 层均匀放大 = 全局学习率/步长问题），不在数据与任务；重训请沿用仓库既有可用的 `--lr 0.00001 --lr-final 0.00001`（上一枚可用 state 就是该设置在 630 行上训出的）。
3. 想加大学习强度，先加 epochs（36 行上几十个 epoch 都在合理范围）并调小 `--save-every` 留 checkpoint，但 lr 保持 1e-5；每个 checkpoint 先过 RMS + canary 可读性两道门，再上评测。
4. 看 loss 的同时看样本：退化训练的 loss 会"跌得很顺"，因为输出越来越可预测。

## 追加：state_out_A2（37 行、108 步）——焊接在推进，但仍在常数基线之下

用户换参数重训（输出落在 `state_out_A/`，00:17 写入的 step-18/36/54/72/90/108，`state-final.pth` == step-108，sha256 `5b1ae832…`）。六个 checkpoint 全部上传跑 workbank S0 40 题；另补一组 `nudge=none`。焊接口径：与语料锚点同 prompt 的**首步一致率**（工具名 / (工具,参数) 精确 / 整回合字节）。

| 臂 | 中位 RMS | 首步一致 名 | 精确 | 整回合 | 通过 | 首步无调用 | 首步 list_files | 工具种类 | canary 可读 | 指纹稳 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 参考：上一枚 state-final | 0.0011 | 11 | 1 | 1 | 1/40 | 3 | 8 | 9 | 是 | 是 |
| A2-18 | 0.84 | 0 | 0 | 0 | 0/40 | 40 | 0 | 0 | 否（日期复读） | 是 |
| A2-36 | 1.02 | 0 | 0 | 0 | 0/40 | 40 | 0 | 0 | 否（33 题碎片复读） | 否 |
| A2-54 | 1.04 | 6 | 0 | 0 | 0/40 | 2 | 0 | 2 | 是 | 是 |
| A2-72 | 1.05 | 5 | 0 | 0 | 0/40 | 10 | 0 | 2 | 否 | 是 |
| A2-90 | 1.06 | 10 | 1 | 1 | 0/40 | 6 | 5 | 4 | 否 | 否 |
| A2-108 | 1.06 | **18** | **4** | **4** | 0/40 | 1 | 24 | 4 | 否 | 否 |
| A2-108 + `nudge=none` | 1.06 | 18 | 4 | 4 | 0/40 | 1 | 24 | 4 | 否 | 否 |
| （基线）零 state | — | 7 | 2 | 0 | 3/40 | 17 | 6 | 9 | 是 | 是 |
| （常数基线）恒选 list_files | — | **22** | 9 | — | — | — | 40 | 1 | — | — |

读数：

1. **焊接确实在推进**：首步一致率随步数 0→6→10→18（step 18→108），远超基座的 7/36；但 **18/36 仍低于"恒选 list_files"的常数基线 22/36**，精确 (工具,参数) 4/36 也低于基线 9/36。也就是说，还没到"把 36 条首步记下来"的程度。
2. **没有任何 checkpoint 拿到通过**（0/40）。失败画像与上一枚 state 同类：answer 阶段协议错 25、plain-number 契约 17（这四个臂全都是 17，是跨臂常数）、值不符 10；变化的是 step 用尽从 5 降到 0。
3. **连贯性与焊接同向恶化**：canary 从 step 36 起基本不可读（step 54 例外），指纹从 step 36 起时稳时不稳；A2 幅度（RMS 1.06）只有上轮 A（3.83）的 1/3.6，所以没有词沙拉式崩溃，但已明显偏离可用区。
4. **`nudge=none` 不改变焊接与通过**（18/36、0/40 与默认 wire 完全一致）——再次说明当前瓶颈不在转写形态。

结论：这轮参数让 state 走在了"能焊、但还没焊到、同时开始失真"的区间。若目标是**通过数**，继续加大焊接不是方向——真正的堵点在轨迹末端（何时收尾、答案契约）；若目标是**验证焊接上限**，应从 step-108 继续同参数多跑 300+ 步，看一致率能否越过 22/36，同时接受模型进一步失真。

## 追加：state_out_B（700 行、lr 0.03、6 epochs）——第一个真正可用的 state

训练命令（用户提供）：`--data train.textonly.jsonl --ctx 4096 --chunk 1024 --wkv_tape --batch-size 8 --epochs 6 --lr 0.03 --lr-final 0.005 --warmup-steps 10 --save-every 78`，700 行，输出 `state_out_B/`（step 78/156/234/312/390/468 + final，final sha256 `6814f133…`）。

**这是本项目 workbank 历史上最好的一次：final 通过 14/40（零 state 基线 3/40），协议有效率 0.96。** 七个 checkpoint 全部上传并跑完 workbank：

| checkpoint | 中位 RMS | workbank | 有终答 | 协议有效 | 首步一致（名/精确/整回合） | canary 稳 |
|---|---:|---:|---:|---:|---|---|
| B-78 | 0.137 | 1/40 | 6 | 0.80 | 19 / 8 / 8 | 是 |
| B-156 | 0.145 | 6/40 | 20 | 0.86 | 22 / 8 / 8 | 否 |
| **B-234** | 0.154 | **15/40** | 34 | 0.94 | 22 / 8 / 8 | 否 |
| B-312 | 0.160 | 9/40 | 37 | 0.97 | 21 / 6 / 6 | 是 |
| B-390 | 0.166 | 11/40 | 33 | 0.94 | 25 / 9 / 9 | 是 |
| B-468 | 0.174 | 10/40 | 32 | 0.94 | 25 / 9 / 9 | 是 |
| B-final | 0.176 | **14/40** | 35 | **0.96** | 22 / 8 / 8 | 是 |
| （对照）零 state | — | 3/40 | 20 | 0.76 | 7 / 2 / 0 | 是 |
| （对照）上一枚 state-final | 0.001 | 1/40 | 9 | 0.74 | 11 / 1 / 1 | 是 |
| （基线）恒选 list_files | — | — | — | — | 22 / 9 / — | — |

对照 A/A2：state 幅度全程停在 **RMS 0.137→0.176** 的窄带内（A 0.84→3.9 崩溃、上轮 A 3.8 词沙拉），随步数单调微增，canary 大部分稳定。**同样的"大 lr"思路，这批参数落在可用区。**

三条关键读数：

1. **通过数与轨迹形态一起变好**：失败画像里 answer 阶段协议错 23→4、plain-number 契约 17→6；首步从"必调工具/偏网页"回到本地优先（read_file 67、calculator 30、list_files 28、web_search 22），首步 `list_files` 24/40。
2. **焊接达到并略超常数基线**：首步一致率 19→25/36（基线 22/36），精确 (工具,参数) 6–9/36（基线 9/36）；语料首决策探针 24 条里工具名一致 **18/24 = 75%**、格式 24/24（基座 1/24、0/24）。即这枚 state **既装上了語料策略、也真的做对了题**——与前几轮"只装形态"不同。
3. **代价是严重的通用能力遗忘**：BFCL product 从零 state 的 **47/60 掉到 13/60（B-234）/ 7/60（B-final）**；boundary 0/18→4/18。workbank 的收益与 BFCL 的损失同向增长，越往后训 BFCL 越差。

另测：`nudge=none` 下 B-final 是 12/40（默认 wire 14/40），提醒仍然略有帮助；`B-234` 与 `B-final` 的差（15 vs 14）在单次贪心 n=40 的噪声量级内，但 **B-234 的 BFCL 明显更好（13 vs 7）**，若要兼顾通用能力，应取更早的 checkpoint。

结论与建议：

- 这套参数（lr 0.03 + warmup 10 + lr-final 0.005、batch 8、6 epochs、700 行）可以作为**新的训练基线**固化；之前 A/A2 的 0/40 是幅度失控（RMS 0.84–3.9）所致，不是"极限学习"本身不可行。
- 若目标是 workbank 分数：曲线在 156→234 仍在上升，312–468 的 9–11 落在噪声带内，**建议在 6 epochs 之上再加密 checkpoint 继续跑**，同时盯住 BFCL 的退化速度。
- 若目标是可交付的通用 agent：需要混入通用工具调用数据（BFCL 风格）做正则或回放，否则这是典型的"专精换遗忘"。
- 评测记录：B 各 checkpoint 的 workbank 在 `runs/state-check-20260920/b-{78,156,234,312,390,468,final}-s0-20260921-workbank/`，回归在 `b-final-s0-20260921-{boundary,bfcl}/` 与 `b-234-s0-20260921-bfcl/`，剂量-反应 JSON 在 `analysis/b-dose-response.json`（`runs/` 为 ignored，下表已收录其全部数字）。B-156/B-234 两次 run 触发严格 canary 漂移（effective 稳定），已按 `--allow-canary-drift` 记录。

## 追加：高分轮（B-234 / B-final）的轨迹逐题体检——损失在哪里，不在哪里

用户提问：高分那几轮的轨迹里有没有绕路、有没有输出语序问题。逐题拉出 29 道通过题的完整轨迹（工具序列 + 参数 + 终答），与语料锚点的参考轨迹对齐比较，并把生成文本（终答、写文件内容、检索词）与零 state 同题对照。

### 1. 绕路：几乎不存在，29 道里 22 道不比语料参考更长

| 绕路 delta（调用数 − 语料参考调用数） | −3 | −2 | −1 | 0 | +1 | +2 | +4 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 题数 | 1 | 4 | 6 | 11 | 5 | 1 | 1 |

均值 −0.21。也就是说通过题的轨迹**不比语料给的参考路径长**，11 道与参考步数完全相同。两处明显绕路：

- `web-0004`（B-234，+4）：`web_search → web_fetch → web_fetch → read_file → list_files → web_fetch×3`，中途从网页任务折回本地目录，还触发 1 次 duplicate，最终仍答对 256。
- `doc-0003`（B-234，+2）：先用两次 `web_search` 找公司报销政策，再回本地读 `policy/expense-policy.md`，最后按契约答 `UNKNOWN`（该题允许）——**"先搜网页"的残留习惯仍在**，只是不再致命。

另外三处小的重复：`doc-0002`、`hyb-0001`、`web-0002` 各把同一个 `web_search` 发了两次（无 duplicate 拒绝），仍通过。

### 2. 措辞/语序：没有发现退化，反而是收敛

| 指标 | 零 state | B-234 | B-final |
|---|---:|---:|---:|
| 非空终答 | 20/40 | 34/40 | 35/40 |
| 终答平均长度 | 81 字符 | 6 字符 | 10 字符 |
| >120 字符的终答 | 2 | 0 | 0 |
| 含非 ASCII | 0 | 0 | 0 |

答案从"散文解释"收敛成契约值（`950`、`4417`、`config/history_retention.yaml`、交付题用 `DONE`、弃权用 `UNKNOWN`），这正是通过率上升的主要原因。生成的长文本也干净：`doc-0001` 的 `tasks/todo.md`、`doc-0004` 的 `ops/checklist.md` 都是语法正确、排版规整的 Markdown；检索词也地道（`expense report window days after end of business trip`、`oxcart batch_size default`）。**语序/语法退化没有出现在任何一处生成文本里。**

### 3. 损失确实存在，但在"何时行动"而不是"怎么说话"

去 BFCL 的翻转题里看就很清楚（零 state 过、B-final 挂的 41 题）：

| BFCL 类别 | n | 零 state | B-234 | B-final |
|---|---:|---:|---:|---:|
| irrelevance（只需直接回答） | 20 | 10 | 2 | 1 |
| missing_simple_python（缺参应追问） | 10 | 10 | 8 | 0 |
| recovery_multi_turn | 10 | 10 | 1 | 2 |
| state_multi_turn | 10 | 9 | 0 | 2 |
| supplied_simple_python | 10 | 8 | 2 | 2 |

| 行为指标（BFCL 60） | 零 state | B-234 | B-final |
|---|---:|---:|---:|
| 该直答却调了工具 | 2 | 18 | **26** |
| 工具参数全部非法 | 0 | 4 | **15** |
| 出现 duplicate 拒绝 | 2 | **46** | **50** |
| 空终答 | 6 | 43 | 20 |

典型轨迹（`bfcl_irrelevance_2`，题目是解一元二次方程）：

- 零 state：0 次调用，直接给出求根公式与结果 → 通过。
- B-final：`calculator({"expression":"3*x^2-5","precision":6})` → 参数非法 → **原样再发一次** → duplicate → 强制收尾 → **空终答**。

`bfcl_irrelevance_4` 更典型：`calculator → calculator → list_files → read_file → list_files`，兜了一圈答 `Insufficient`。

**两个机制**：(a) 语料里没有"不需要工具"的锚点（36 个锚点全是工具题），所以 state 学到的是"先取证再回答"这条无条件规则，workbank 的 4 道 nt 题 4/4 过度调用、BFCL irrelevance 26/60 过度调用；(b) 工具报错后不修复、原样重发，在 workbank 里被训练分布压到 7/40，出了分布立刻反弹到 50/60。

### 4. 结论

- **绕路**：存在但很小（均值 −0.21，22/29 不比参考长），主要是"先搜网页"的残留和偶发重复检索，不再决定成败。
- **语序/措辞**：没有退化证据；输出反而更规整（终答契约化、长文本语法正确）。
- **真正的损失**是策略层面的两条：无条件先调工具、报错后重复而不修复。这解释了"workbank 涨、BFCL 塌"，也说明下一步该补的是**语料里的 no-tool 判例与工具报错后的修复判例**，而不是语言质量。

## 对照：仓库里已有的 DeepSeek workbank 成绩

用户问起的 DeepSeek 成绩都在仓库里，分三处存着：报告 `bench/workbank/reports/matrix-pilot40.md`（试点判决）、原始 run `runs/workbank/*deepseek*/`、账本 `bench/workbank/ledger/runs.jsonl`。

配置：DeepSeek 走 `--completion chat-completions` + 自己的原生 wire（v1 `bc79a316`、v2 `67a54f2e`），模型 `deepseek-v4-flash`，每题跑 k=4；端点按当时本地凭据配置，未记入本文档。G1K 走 XML wire（`51859aff`/`06b63561`…），单跑贪心。

| 轮次 | 用例库 | max-steps | k=4 逐次通过 | 均值 | L0 / L1 / L2 | 备注 |
|---|---|---:|---|---:|---|---|
| DeepSeek v1（试点首发） | `sha256:663…` | 6 | 20 / 21 / 19 / 19 | **49.4%** | 80% / 50% / 20% | 极差 5.0pp；闸门②当时按"去 nt/scr"口径通过 |
| DeepSeek v2（修题+预算后） | `sha256:d87…` | 10 | 25 / 29 / 24 / 24 | **63.5%** | 80% / 62% / 50% | **极差 12.5pp → 闸门①失败**（N=40 的测量学问题） |
| DeepSeek closeout 单跑 | `sha256:324…`（**= 当前用例库**） | 10 | 30 / 40 | **75%** | 80% / 80% / 60% | 与我们现在跑的 40 题**同一版**用例库（已逐题核对 nt-0001/scr-0001/tab-0004 文本一致） |
| G1K 零 state（对照） | 同上 | 10 | — | 2.5%（v1/v2 库）；当前库单跑 3–4/40 | 10% / 10% / 10% | 我们这两轮的重测 |

另有两组非对照用途的 DeepSeek run 在库里：`deepseek-solve-k0/k1`（steps 8，15/40、13/40）是**求解检查**轮（用于给 45 条标签定"题目可解"基线），`postfix-deepseek-k0..k3` 是 5 题修复验证（0/0/0/1）。

### 同库同预算的直接对照（当前 40 题、max-steps 10）

| 臂 | workbank | L0（10 题） | L1（20 题） | L2（10 题） |
|---|---:|---:|---:|---:|
| DeepSeek closeout 单跑 | **30/40（75%）** | 8/10 | 16/20 | 6/10 |
| DeepSeek v2 k=4 均值 | 25.5/40（63.8%，前一版用例库） | 32/40 | 50/80 | 20/40 |
| G1K state **B-234** | 15/40（37.5%） | 4/10 | 8/20 | 3/10 |
| G1K state **B-final** | 14/40（35%） | 5/10 | 8/20 | 1/10 |
| G1K 基座（最好 wire） | 4/40（10%） | 1/10 | 2/20 | 1/10 |

**即：这枚 state 把 G1K 从 10% 拉到 35–37.5%，约为 DeepSeek 同库成绩的一半；分档看差距主要在 L2（1–3/10 vs 6/10）与 L1（8/20 vs 16/20）。**

### 逐题对照：state 赢在哪、差在哪

拿 DeepSeek v2 最好的一跑（k1，29/40）与 B-final（14/40）比对：

- 两者都过：11 题（cfg-0002/cfg-0004/doc-0001/doc-0002/fs-0002/fs-0003/hyb-0001/log-0001/scr-0001/web-0001/web-0002）
- 只有 DeepSeek 过：18 题（cfg-0001、code-0001/0003、doc-0003、doc-0004、fs-0001、fs-0004、hyb-0003、log-0002/0003/0004、scr-0002/0003、tab-0001/0003/0004、web-0003、web-0004）
- **只有 state 过：3 题（cfg-0003、hyb-0002、tab-0002）**
- 四道 nt 题（no-tool 场景）**DeepSeek 也全灭（0/4）**——它同样反射式调工具；反而 G1K 基座因为"不太会调工具"拿下了 nt-0002/0003/0004。

也就是说 state 的通过集合基本是 DeepSeek 通过集的子集（11/14 重合），外加 3 道 DeepSeek 也做不出的题；差距集中在需要多步取证 + 精确汇总的 L2、以及需要工具纪律的 L1。

### 口径提醒

- DeepSeek 是 k=4 采样跑（每跑独立），我们的 state 是单次贪心；比较均值 vs 单点时要留意 ±2–3 题的抖动。
- wire 不同（DeepSeek 原生 chat-completions vs G1K XML 单阶段），这是两套模型各自的自然形态，不是同一 wire 的对比。
- v1(663)/v2(d87)/closeout(324) 是三版用例库；**只有 closeout 那版与当前一致**，逐题比较优先用它或重跑。

若要重跑 DeepSeek：用 `--completion chat-completions`、模型 `deepseek-v4-flash`（端点填入你自己的 chat-completions 服务），套件参数与 state 轮保持一致（`--cases bench/workbank/cases --tool-catalog work-v1 --file-tools lines --max-steps 10 --case-parallelism 40 --case-timeout 30m`），跑完把 run 目录给我即可并入本表。

## 产物与复现

- 运行数据：`runs/state-check-20260920/{zero,final}-s0-20260920-{workbank,boundary,bfcl}/`（summary/run.json/experiment.json + 日志）
- 逐项对照：`runs/state-check-20260920/analysis/comparison.json`（`analysis/compose.py` 生成）
- 通过题轨迹体检：`bench/workbank/reports/state-passing-trajectories-20260921.json`
- A2 剂量-反应数据：`runs/state-check-20260920/analysis/a2-dose-response.json`；各 checkpoint 运行目录 `runs/state-check-20260920/a2-{18,36,54,72,90,108}-s0-20260921-workbank/` 与 `a2-108-nonudge-20260921-workbank/`
- 焊接率度量：`bench/workbank/tools/measure_anchor_agreement.py`（首步 名/精确/整回合 一致率 + 常数基线）
- outA 扫描数据：`runs/state-check-20260920/outA-{45,90,135,180,225,270}-s0-20260920-workbank/`（六个 checkpoint 的 workbank 结果）
- 提醒消融：`runs/state-check-20260920/{zero,final}-nonudge-s0-20260920-workbank/`（`--wire nudge=none`，wire_hash `625533bb…`）
- 轨迹拆分：`runs/state-check-20260920/analysis/decomposition.json`（`analysis/decompose.py` 生成：首步动作对照、阶梯转移矩阵、锚点路径命中）
- 探针：`runs/state-check-20260920/corpus-probe-firststep.json`（首决策）、`corpus-probe.json`（收尾位）
- 上传回执：`runs/state-check-20260920/state-final.pth.upload.json`
- 锚点行导出（36 条评测同 prompt 的训练集）：`outputs/workspace-agent-700-anchors36-state-tune/`（`manifest.json`/`identity.md`/`first-steps.md`/`README.md` + textonly/rendered JSONL；逐行首步工具、参数与完整工具序列都在 manifest 里）
- 新增/改动脚本：`scripts/state-corpus-probe.py`、`bench/workbank/tools/extract_anchors.py`、`bench/workbank/tools/state_sanity.py`（新增）；`scripts/state-experiment.py` 增加可选 `--root`（默认值不变，本轮用 `--root runs/state-check-20260920`）

```sh
python3 scripts/state-experiment.py zero-s0-20260920 \
  --credentials <creds.json> --root runs/state-check-20260920 --suites workbank
python3 scripts/state-experiment.py final-s0-20260920 --state-id state-final.pth \
  --credentials <creds.json> --root runs/state-check-20260920 --suites workbank
python3 scripts/state-corpus-probe.py --split first --rows 24 --stride 26 \
  --credentials <creds.json> --output runs/state-check-20260920/corpus-probe-firststep.json
python3 runs/state-check-20260920/analysis/compose.py && python3 runs/state-check-20260920/analysis/decompose.py
# 导出 36 条锚点行（--scope family|all 可换成整族/全部）
python3 bench/workbank/tools/extract_anchors.py outputs/workspace-agent-700-anchors36-state-tune --scope anchor
```
