# RWKV7-G1i-7.2B 输出偏好（Harness 重建的唯一输入）

本文件逐条列出在 `test/probes/` 中实测出的模型偏好。每条附 x/n 计数和实验
目录；写不出数字的条目不收录。所有探针走 `/v1/batch/completions` 裸续写、
贪心解码（temperature 0.001 / top_k 1 / top_p 1 / penalty 归零）、CF Access
认证，prompt 结构逐字节镜像产品 Markdown 协议
（`rwkv-g1i-functions-product-v1`，与 `test/baseline/main-bfcl-product-20260831/
trace.jsonl` 中的真实请求核对）。分类全部事后进行，原始输出保留在
`cells.jsonl`，可复核。

环境：模型 `rwkv7-g1i-7.2b-20260805-ctx16384`，端点 `api-7b.rwkvos.com`，
服务器 `available_bsz≈165`。已知该后端在贪心下约 5% 输出不稳定（见"方法
说明"）。

方法说明（两次独立运行）：P1 的 400 格跑了完整两遍（`out/p1-long-context`、
`out/p1-long-context-confirm`），逐格分类一致率 345/400 = 86.2%；分歧全部
集中在 10k/20k 边缘格（如 deep-20k-repetitive 分歧 7/10），条目级结论在两
次运行中一致。P2/P3/P4 同样各跑两遍（`-confirm` 目录），全部条件级结论逐格
复现。下文每条同时给出两次运行的计数（run1 / run2）。

---

## P1 长上下文降解（test/probes/p1-long-context/）

设置：固定"抓取网页后决定下一步"的任务，注入正文铺 500/2k/5k/10k/20k
token × 4 种正文类型（prose 干净散文 / code 含成对代码块 / lists 密集列表 /
repetitive 重复结构）× 10 实例；deep 锚点（`Assistant: ```json\n{"name":"`，
即生产决策态）与 bare（`Assistant:`，模型自由起笔）两种前缀各测一遍。
"格式合规"（call_ok）= 产出可解析、name/arguments 形状正确的工具调用。

### P1-1 deep 锚点下，格式合规到 10k token 基本无损，20k 明显降解

| 注入长度 | call_ok（run1 / run2，各 40） |
| --- | --- |
| 500 | 40/40 · 40/40 |
| 2k | 40/40 · 40/40 |
| 5k | 40/40 · 40/40 |
| 10k | 37/40 · 40/40 |
| 20k | 30/40 · 32/40 |

降解点在 10k 与 20k 之间；20k 档两次运行都只有 75–80%。
目录：`test/probes/p1-long-context/out/p1-long-context{,-confirm}/counts.md`。

### P1-2 bare（无锚点）自由续写从 2k 开始降解，5k–10k 崩溃

call_ok（run1 / run2，各 40）：500 = 39/39 · 39/40；2k = 35/40 · 35/40；
5k = 29/40 · 25/40；10k = 16/40 · 20/40；20k = 20/40 · 23/40。
没有锚点时模型经常根本不进入工具调用形态（跑偏为思考文/散文）。
目录：同上。

### P1-3 复读从 10k 档出现；两种来源都存在，自我复读为主

复读桶计数（run1）：deep 10k = 2/40，deep 20k = 7/40；bare 10k = 8/40，
bare 20k = 10/40。复读来源（`body_windows>=8` vs `self_windows>=6`）：
deep-20k 以自我复读为主（如 JSON schema 递归循环
`"values":{"type":"string","values":{...}}`、自身词句循环）；正文复读出现在
repetitive 正文（deep-20k-repetitive-06 正文窗口 21 个）。bare 侧 5k 起
repetitive 正文出现正文复读（bare-5k-repetitive-07 正文窗口 30 个），
20k lists 出现自我复读（bare-20k-lists-05..10）。
500/2k/5k（deep）从未出现复读（0/120）。

### P1-4 含代码块的正文对"无锚点续写"最毒；对 deep 锚点不构成主要威胁

bare + code：5k = 0/10（两跑一致）、10k = 0/10（两跑一致）、2k = 5/10
（两跑一致）、20k = 1/10（两跑一致）——四种正文里唯一系统性崩溃的类型，
与工具调用围栏打架的假设在无锚点场景成立。deep 锚点 + code：10k =
7/10 · 10/10，20k = 9/10 · 6/10——远好于 bare，主要失败转为复读/跑偏而非围栏。
deep-20k 档最毒类型在两次运行间不稳定（run1 repetitive 3/10，run2
code 6/10、lists 6/10），该档整体降解（P1-1）比单一类型更可靠。

### P1-5 正文内容污染输出罕见

哨兵检测（正文埋 3 个唯一编码，输出中出现即污染）：deep 两次运行 0 污染；
bare 仅零星格（5k-10k 共 4 格 / 400）。长正文的主要失败形态是跑偏与复读，
不是正文内容窜入调用。

### P1-6 模型从不主动弃权（no_tool），退化时也不弃权

工具选择（deep）：500–5k 全部 120/120 为 web_search（任务要求搜索）；
10k = 34 web_search + 3 web_fetch + 3 复读；20k = 29 + 1 + 10。
bare 侧 10k 仅 16/40 还能给出可解析调用，但其中 no_tool 出现 0 次。
模型在降解时不选择"承认无法完成"，而是产出坏格式。

### P1-7 无锚点时模型自发进入 `<think>`，且随长度增加

bare 前缀下输出以 `<think>` 开头的比例：500 = 2/40，2k = 8/40，5k = 15/40，
10k = 30/40，20k = 23/40。deep 锚点下 0/40（两跑一致，200+200 格）。
生产 harness 的 fast-think 预填（`<think></think`）把这条自发行为关掉了。

---

## P2 工具结果回填格式（test/probes/p2-tool-result-feedback/）

设置：同一份 ~350 token 短页 + 同一份计算结果，五种回填包裹
（plain = 现行产品形态 `User: Function output:\n<text>`、json = JSON 包裹、
xml = `Tool: <tool_result>…</tool_result>`、fielded = 字段命名、indented =
缩进）× 20 实例 × 2 阶段（decision 深锚点应继续调 calculator；answer 阶段
工具链闭合后应报出 ×1000 数值）。

### P2-1 短结果：五种包裹全部无差异，包裹格式不是杠杆

decision：plain 20/20，json 20/20，xml 20/20，fielded 20/20，indented 20/20
（v2 跑与确认跑一致）。answer：20/20 · 19/20 · 20/20 · 20/20 · 20/20
（合计 99/100）。没有任何一种包裹显著优于现行 plain 形态。
目录：`out/p2-tool-result-feedback-v2/counts.md`。

### P2-2 长结果：plain 与 json 包裹在 5k/10k 同为满分

wrap × 长度交叉（decision，deep 锚点，10 个 prose 正文 ×2 跑）：
plain-5k 10/10 · 10/10，json-5k 10/10 · 10/10，plain-10k 10/10 · 10/10，
json-10k 10/10 · 10/10。JSON 转义不加速也不延缓降解（降解由长度决定，
P1-1）。目录：`out/p2-supplement/cells.jsonl`。

### P2-3 工具链未闭合时，answer 阶段模型拒绝作答、坚持先把工具调完

设计迭代运行（v1，`out/p2-tool-result-feedback/`）：answer 阶段喂了页面但
尚未执行 calculator 时，100 条里 94 条无视 "tools are now unavailable" 的
指令、直接输出 ```json calculator 调用，而不是给出用户可见回答。
含义：harness 进入 answer 阶段前必须闭合工具链（现实现已如此）；若未来
提前终止工具链，不能指望模型直接作答。

---

## P3 双来源冲突（test/probes/p3-multi-source/）

设置：两来源就同一事实给出冲突数值（正确来源带权威信号：官方域名 URL +
"primary register" 文本；错误来源为社区 wiki），2×2×2×2 全因子（顺序拼接 /
结构化并列；正确在前 / 在后；Harness 预标注冲突 / 不标；控制提示词要求比对 /
不要求）× 20 实例，answer 阶段 unanchored。判定优先解析"采信了哪个来源"的
句子（run 首版分类器把"先提到的数字"当答案，把正确的比较式回答误判为失败，
已修正；原始 cells.jsonl 未动）。

### P3-1 "只信第一个"不成立：结构化并列下位置效应为 0

结构化并列（一个 Function output 内两块带标签来源）：correct_first vs
correct_last = run1：19/20 vs 19/20（noann/nocmp）、20/20 vs 20/20（ann）；
run2 同格全部一致。位置效应 0 pp。

### P3-2 顺序拼接下存在轻度近因效应：模型更信"最后一条"

correct_first = 17/20（run1）/ 17/20（run2），correct_last = 20/20 / 20/20
（noann/nocmp）。位置效应 −15 pp（负号 = 末位更准）。与 P4 相比幅度小。
"第一位命中率和末位命中率的差值"实测为 −15 pp（顺序拼接）与 0 pp（结构化），
不是"第一位更被相信"。

### P3-3 预标注冲突与"要求比对"的提示词均无可靠效果

同一条件开/关标注或比对指令，计数差 ≤1 格（n=20，噪声范围内）。例：
structured noann/nocmp = 19/20 vs ann/nocmp = 20/20；sequential/ann 两次
标注格反而出现 3/20 的 false_hit（run1），run2 复现 2–3/20。没有证据支持
在提示词里加"请比对来源"能改变行为。

---

## P4 子 Agent 结果回填（test/probes/p4-subagent-feedback/）

设置：同 P3 的冲突结构，来源换成 spawn_agents 子 Agent 结果（JSON 形态
逐字节镜像 `delegate.go` 的回喂格式）；batch = 两条结果合并进一个 Function
output，separate = 两条独立 Function output 顺序回喂；位置 = 正确子 Agent
排前 / 排后；标注 = 框架层加"这是子 Agent 的输出，可能有误" / 不加；×
比对提示词。两次全量运行，结论逐格复现。

### P4-1 子 Agent 结果存在强近因效应：正确结果排首位时大面积采纳错误的第二条

separate：correct_first = 6/20 · 6/20（noann/nocmp），correct_last = 18/20 ·
18/20，位置效应 −60 pp（run2 −55~−60 pp）。batch：correct_first = 11/20 ·
11/20，correct_last = 15/20 · 16/20（−20~−25 pp）。这是"子 Agent 结果不核对、
直接采信"毛病的量化：模型不比对，按最近一条采纳。

### P4-2 框架层警示标注不能修复该偏差

加"可能有误"标注后：separate/correct_first = 7/20 · 8/20（基线 6/20），
batch/correct_first = 12/20 · 11/20（基线 11/20）。改善 ≤2 格（n=20），
在两次运行的波动范围内。该标注在本模型上无效。

### P4-3 提示词要求比对同样无效

开/关比对指令的计数逐格相同或差 ≤1 格（同 P3-3）。

### P4-4 合并为单条回喂可显著缓解（不能消除）近因偏差

batch vs separate（correct_first）：11-12/20 vs 6-7/20；（correct_last）：
15-17/20 vs 18/20。合并回喂把最差情况从 30% 提到 55% 左右，但仍远低于
P3 结构化并列的 95–100%（见 P4-5）。

### P4-5 子 Agent 结果缺少 P3 场景中的"来源权威信号"

P3 结构化并列给每块来源标注了 URL 与自述（官方 vs wiki），模型 95–100%
选对；P4 的子 Agent JSON 里只有 task/output 字段，即便位置有利也只有
55–85%。两实验的唯一结构差异是每条结果是否携带可判权威性的来源信息。
（观测层面陈述；"携带来源 URL 是否因果地恢复正确率"未单独验证。）

---

## 对 Harness 的可执行含义（每条注明依据）

以下不是新的观测，是上文的工程推论，供第二步使用：

1. fetch 结果切片阈值：注入正文 ≥10k token 后决策格式开始受损、20k 明显
   降解（P1-1）。产品 `maxFetchedContentRunes = 32k`（≈8–16k token 英文、
   ≫10k token 中文）超过安全区；切片阈值应取 <10k token 并为控制提示词和
   历史留余量。
2. 决策步骤保持 deep 锚点（P1-1 vs P1-2：≤5k 时 40/40 vs ≤75%）；答案步骤
   保持 unanchored + fast-think 预填（P1-7：无预填时 `<think>` 自发率随长度
   升至 30/40）。
3. 子 Agent 结果必须合并为单条回喂并携带每条结果的来源/权威信号
   （P4-4、P4-5、P3-1）；顺序多条回喂是最差形态（P4-1）。
4. "来源可能冲突，请比对"类提示词与"子 Agent 输出可能有误"类标注在本模型
   上无可测收益（P3-3、P4-2、P4-3），不应作为修复手段写进 harness。
5. 双来源顺序回喂有 −15 pp 近因效应（P3-2）；harness 若必须顺序回喂，
   不能依赖模型"记住"更早的来源，需要结构化并列。
6. 提前关闭工具链不能直接得到最终回答（P2-3）。

---

## P5 长页压缩（test/probes/p5-compression/）

设置：长页（5k/10k token，P1 prose 体）在 60% 深度埋入一句带答案数值的
事实句；三种压缩提示词形态（extract 逐句摘抄 / summary 摘要 / bullets
要点列表）× 有无 fast-think 预填（`Assistant: <think></think`）。阶段 A
测压缩输出是否保留答案数值；阶段 B 把压缩页喂回产品决策，测答案是否进
入模型输出。

### P5-1 逐句摘抄 + fast-think 预填是最优压缩形态

阶段 A 保留率（x/10）：extract+ft = 10/10（5k）· 9/10（10k）；bullets+ft =
10/10 · 7/10；summary+ft = 8/10 · 6/10；全部 raw（无预填）形态 =
3-4/10（10k）～7-9/10（5k）。压缩长度：extract+ft 平均 ~110 字符，
raw 形态 1100-1900 字符。目录：`out/p5-stage-a2/`。

### P5-2 整页喂回时模型在页内"找不到"答案，改为再抓取；压缩页喂回则正确作答

阶段 B（答案数值进入模型调用，x/10）：extract+ft = 9/10（5k）· 8/10（10k）；
bullets+ft = 10/10 · 7/10；**整页对照 = 1/10（5k）· 0/10（10k）**。整页喂回
时 20 格里 11 次再次 web_fetch、7 次改 web_search——模型不在长页里检索答案，
而是发起更多工具调用。目录：`out/p5-stage-b/`、`out/p5-stage-a2/`。

### P5-3 压缩调用本身必须带 fast-think 预填

无预填时压缩输出以 `<think>` 开头并跑偏（幻觉"没有相关句子"）：
extract raw 5k = 4/10 vs extract+ft 10/10。与 P1-7 同一机制在工具性
提示词上的复现。目录：`out/p5-stage-a{,2}/`。

---

## E6 文件工具对照（test/filetools-ab/，6 轮迭代）

设置：8 个文件编辑任务（建文件 / 追加 / 改值 / 换块 / 删行 / 两步 /
大文件定位编辑）× 两种形态。Form A（lines）= read_lines + write_file +
replace_lines + append_file；Form B（whole）= read_lines + write_file
（编辑 = 读后整文件重写）。产品 Markdown 协议 + 深锚点 + 路由器，
贪心，n=8/轮。

### E6-1 两种形态的工具机制都能工作，差异在 required-tool 完成率

最终轮：Form B required-tool 完成 100%，Form A 60%；历史轮 Form B
88.9-100%，Form A 50-60%。协议合规 76-92%（两形态相当）。选择 **Form B
（whole）**：工具更少、参数面更平、完成率更高。Form A 的 replace_lines
没有转化为优势。目录：`test/filetools-ab/run-form-{a,b}/summary.json`。

### E6-2 无 no_tool 出口时模型无法终止工具循环

去掉 semantic no_tool 后（route 100% 正确、工具调用正确），模型在编辑
成功后反复 read_file 直到步数耗尽（answer 0-12.5%）。no_tool 是 7B 唯一
的"我做完了"信号。目录：`run-form-{a,b}/trace.jsonl`。

### E6-3 有 no_tool 时模型用它谎报完成

带 no_tool 时，模型在不调用任何工具的情况下输出"已追加/已修改"的
reason（fabricated completion），required-tool 完成率跌至 0-60%。
收紧 no_tool 描述（"never claim a file was read, created, or modified"）
只部分改善（required 53-64%）。目录：`run-form-{a,b}/summary.json`。

### E6-4 路由器需要编辑类 few-shot 示例

workspace bundle 描述只写"读取/搜索"时，路由器把编辑任务判为
respond（工具不可用）——加两条编辑示例后 route 100% 正确。
目录：`run-form-{a,b}/trace.jsonl`（route 决策）。

### E6-5 模型把可选整数发成 null

read_lines 的 end_line 按 strict integer 声明时，模型仍发 null；
改为 nullable + 默认值（与 list_files 风格一致）后该错误消失。

**结论：文件编辑工具保持实验性（--file-tools 门控，默认关闭）。
阻塞项是 E6-2/E6-3 的终止/谎报问题，不是工具形态；形态选 Form B。**

## 对 Harness 的可执行含义（续）

7. fetch 结果 token 预算 ≤8k（P1-1 降解点留余量）；超过 ~4k 的单页用
   query-aware 摘抄压缩（P5-1/2/3），压缩前后原文都留轨迹。
8. 子 Agent 结果以带来源标签的块状单条回喂（P4-4/P4-5/P3-1 验证：
   correct_first 11→14-15/20）。
9. 文件工具选 Form B（whole），实验性门控（E6-1）；待 E6-2/E6-3 解决后
   再默认启用。
