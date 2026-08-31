# RWKV7-G1i-7.2B 输出偏好（Harness 重建的唯一输入）

## 对 Harness 的可执行含义（总索引；合并自原三处分节，round-3 起置顶）

以下不是新的观测，是工程推论；依据编号指向下文实测条目。状态更新直接写在
条目内。

1. **fetch 结果切片/预算**：注入正文 ≥10k token 后决策格式开始受损、20k 明显
   降解（P1-1）。fetch 预算取 8192 **真实 token**（round-3 起用真词表进程内
   计数；估算器只在无词表时作预算回退——早切方向安全，实测偏差列表/CJK
   −2~−4%、英文 +16~+40%，见 round-3 报告第一节）。
2. **决策步骤保持 deep 锚点**（P1-1 vs P1-2）；答案步骤保持 unanchored +
   fast-think 预填（P1-7）。
3. **子 Agent 结果必须合并为单条回喂并携带来源/权威信号**（P4-4、P4-5、
   P3-1）；顺序多条回喂是最差形态（P4-1）。块状回喂的 e2e 兑现被第二轮
   撤回（与原始 JSON 打平），保留依据是探针层证据。
4. **"请比对来源"类提示词与"可能有误"类标注在本模型上无可测收益**（P3-3、
   P4-2、P4-3），不应写进 harness。
5. **双来源顺序回喂有 −15pp 近因效应**（P3-2）；必须顺序回喂时不能依赖模型
   记住更早来源，需要结构化并列。
6. **提前关闭工具链不能直接得到最终回答**（P2-3）；P6 进一步实测：大文件
   回喂下答案阶段指令本身也常被违反（P6 节）。
7. **>4096 真实 token 的单页用 query-aware 压缩**（P5-1/2/3）。阈值 round-3
   起按真实 token 计（估算制下实际落点英文 ~3.0k，round-3 报告第一节）。
   压缩输出必须过退化检测（复读循环 → 回退原页）并按页语言切指令；原文
   永远留轨迹。（round-3 落地，报告第二节。）
8. **文件编辑工具选 Form B（whole），保持 --file-tools 门控默认关闭**（E6-1）；
   E6-2/E6-3 的终止/谎报两难未解，且被第二轮证明不是 e2e 分数的主要杠杆。
9. **catalog 参数占位符绝不能给模型可复制的 schema 形状**（E6-7 及 round-3
   残余：{"type":["integer","null"]} 在中文任务下被逐字复制为参数值，web_search
   连续被拒到步数耗尽）。标量/union 拍平为可读字符串（"optional integer
   1..10"），且数值字段解码端必须容忍字符串形式的数字（round-3 窗口 B 实证：
   拍平后模型发 "10" 字符串）。
10. **压缩输出的中文指令已按语言切换**（P5-ZH-1/2；round-3 落地），配合退化
    检测；中文三臂端到端 post 10/10 vs off 0/10（round-3 报告第三节）。回声
    剥离单独无效（阶段 B raw 11/20 vs strip 10/20，阴性结果如实保留）。
11. **检索纪律是下一杠杆，不是终止机制**：循环地板的失败是"没找到"（第二轮
    §四）。P6 探针（round-3）把成因拆开：检索工具零主动使用、决策端充分性
    判断失败、跨轮遗忘（含自信否认形态）——见 P6 节。

本文件逐条列出本轮临时实验中实测出的模型偏好。每条附 x/n 计数；写不出
数字的条目不收录。所有探针走 `/v1/batch/completions` 裸续写、
贪心解码（temperature 0.001 / top_k 1 / top_p 1 / penalty 归零）、CF Access
认证，prompt 结构逐字节镜像产品 Markdown 协议
（`rwkv-g1i-functions-product-v1`，并与当时保存的真实请求核对）。分类全部
事后进行；原始临时工作区已从源码仓库及其重写后的历史中清除，量化结论保留
在本文和三份 Harness 报告中。

环境：模型 `rwkv7-g1i-7.2b-20260805-ctx16384`，端点 `api-7b.rwkvos.com`，
服务器 `available_bsz≈165`。已知该后端在贪心下约 5% 输出不稳定（见"方法
说明"）。

方法说明（两次独立运行）：P1 的 400 格跑了完整两遍（`out/p1-long-context`、
`out/p1-long-context-confirm`），逐格分类一致率 345/400 = 86.2%；分歧全部
集中在 10k/20k 边缘格（如 deep-20k-repetitive 分歧 7/10），条目级结论在两
次运行中一致。P2/P3/P4 同样各跑两遍（`-confirm` 目录），全部条件级结论逐格
复现。下文每条同时给出两次运行的计数（run1 / run2）。

---

## P1 长上下文降解

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
对应的原始逐格文件已随临时实验工作区清理。

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

## P2 工具结果回填格式

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

## P3 双来源冲突

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

## P4 子 Agent 结果回填

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

## P5 长页压缩

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

## E6 文件工具对照（6 轮迭代）

设置：8 个文件编辑任务（建文件 / 追加 / 改值 / 换块 / 删行 / 两步 /
大文件定位编辑）× 两种形态。Form A（lines）= read_lines + write_file +
replace_lines + append_file；Form B（whole）= read_lines + write_file
（编辑 = 读后整文件重写）。产品 Markdown 协议 + 深锚点 + 路由器，
贪心，n=8/轮。

### E6-1 两种形态的工具机制都能工作，差异在 required-tool 完成率

最终轮：Form B required-tool 完成 100%，Form A 60%；历史轮 Form B
88.9-100%，Form A 50-60%。协议合规 76-92%（两形态相当）。选择 **Form B
（whole）**：工具更少、参数面更平、完成率更高。Form A 的 replace_lines
没有转化为优势。原始逐轮文件已随临时实验工作区清理。

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

### E6 补充（class-3 e2e 期间实测）

| 编号 | 结论 | 数据 |
| --- | --- | --- |
| E6-6 | 路由器对 delegate 请求同样需要 few-shot 示例，否则判为 respond | 加 delegation 示例前 2/3 任务路由错误；加后全部正确路由 |
| E6-7 | **模型会把 catalog 里数组参数的嵌套 schema 当成参数值复制**（`tasks == {"items":...,"type":"array"}`） | catalog 平铺为 `"array of string"` 后该失败消失（`internal/agent/g1i_functions.go` makeG1ICatalogEntry） |

## P5-ZH 中文长页压缩（第二轮 2026-08-31）

设置：真实中文网页文本（zh.wikipedia 28 篇，词表真实分词），5k/10k token 页，
60% 深度埋一条带数值的事实句（虚构天文台名 + 唯一数值），10 实例/格；压缩
提示词形态 × fast-think 预填；阶段 A 测压缩输出的数值保留，阶段 B 把压缩页
喂回深锚点产品决策测数值进入模型输出。分类全部事后进行（数字做千分位/全角
归一化），原始 cells.jsonl 保留。

| 编号 | 结论 | 数据（run1，n=10/格） |
| --- | --- | --- |
| P5-ZH-1 | **逐句摘抄（extract）形态在中文长页上系统性触发逐字复读循环**：现行 harness 英文指令+fast-think 保留率崩到 2/10·2/10（英文同形态 P5-1 为 10/10·9/10）；8 种中英文指令变体全部 ≤8/10，且 10k 档普遍劣于 5k | extract-en+ft：2/10·2/10；extract-zh：2/10·0/10；extract-zh-v2（禁重复）：5/10·3/10；v3（限五句）：4/10·0/10；bullets：6/10·2/10；quote（单句）：8/10·2/10。失败形态：同一句子原样重复抄录直到 256 token 预算截断，60% 深度埋点句从未到达 |
| P5-ZH-2 | **内容锁定的摘要是最优中文形态**（≤3 句、只用页面原文词句、不提及子任务、无开场白）+ fast-think：保留率 10/10·9/10，平均 167-367 字符，与英文 extract+ft 相当；无约束摘要 9/10·7/10 但输出是"子任务回声"元文本（"该数字已被找到，为N人次"），阶段 B 不可用 | clean-summary-zh+ft：10/10·9/10；summary-zh（无约束）：9/10·7/10 |
| P5-ZH-3 | **中文决策阶段本身没有问题，瓶颈在压缩输出形态**：把埋点句原文单独喂回决策 → 20/20、0 次再搜索；clean-summary 压缩页喂回只有 6/10·6/10（残余回声/开场白输出触发再搜索）；现行英文 extract 指令的压缩页喂回 2/10·1/10；整页对照 0/10·0/10（复现 P5-2） | fact-only：10/10·10/10；clean-summary-zh-ft：6/10·6/10（再搜索 4/10·7/10）；extract-en-ft：2/10·1/10；full：0/10·0/10 |
| P5-ZH-4 | 分类方法修正：模型在决策阶段用英文作答时把 6412 写成 "6,412"，原始子串计数会漏判成功；涉及数值的计数必须做千分位/全角归一化 | 归一化前 clean-summary 阶段 B 计为 3/10·3/10，归一化后 6/10·6/10 |

## P6 检索纪律分解（第三轮 2026-08-31）

设置：英文任务（find the annual visitor count ... in the workspace files），
5 个 report-*.txt 的真实 prose 正文（真词表逐 token 标定），事实句带唯一
5 位数埋在指定文件指定深度，list_files/read_file/search_text 回喂格式逐字节
镜像 runtime（read_file 整读、结果为紧凑 JSON）。decision 格用 deep 锚点、
answer 格用 PrepareAnswer 同款指令（unanchored）。n=10/格，320+80 格。
分类事后进行（classify.py，含千分位归一化），原始 cells.jsonl 保留。

| 编号 | 结论 | 数据（run1） |
| --- | --- | --- |
| P6-1 | **search_text 零主动使用**：拿到含文件大小的 list_files 结果后，模型从不用 search_text 规划检索，而是按序整读（report-1.txt 起）；给不给 search_text、文件小（5×600）还是大（5×2500）完全不改变这一偏好（0/40）。e2e 循环里出现的 search_text 是读取失败后的被动反应，不是检索规划 | 4 条件（大小×有无 search）×10：全部首个动作 = read_file report-1.txt |
| P6-2 | **决策端"充分性判断"失败是循环主驱动**：把整份事实文件（含答案）读完喂回后，决策端仍以 search_text 继续而不是 no_tool 收尾（单文件 3 档深度 8-10/10 继续；5×1.5k 多文件 no_tool 仅 0-4/10）。答案能力与收尾判断解耦：强制 answer 格携带率 8-10/10 | c1f2500d1：search 10/10，answer 8/10；c2：search 9/10，answer 10/10；c6/c7：no_tool 7/10·2/10，answer 10/10·10/10 |
| P6-3 | **整读回喂下的页内提取基本完好，但随埋点深度尾部衰减**：事实在最后一份被读文件里时，answer 携带率 10/10（深度 10%/60%）、6/10（深度 90%）；单文件 2.5k 档 8-10/10。"读回来了定位不到"不是多文件失败的主成因 | c6/c7 vs c8：10/10·10/10 vs 6/10；c1-c3：8/10·10/10·8/10 |
| P6-4 | **读了就忘（跨轮遗忘）实测成立且形态危险**：同一 5×1.5k 负载，事实文件从最后读改为第 1/第 3 个读（后随 4/2 次其他读取），answer 携带崩到 6/10·0/10；失败形态包括**自信否认**（"The 2024 operations summary is not present in any of the workspace files"——事实逐字在上下文里）、幻觉路径（.github/workflows/ci-cd.yml、path:"none"）、答案阶段 <think> 跑偏。P4-1 近因偏差在文件域的复现，且解释多文件 e2e 循环：早先读到的内容对后续决策功能性失效 | d1factfirst 6/10（其中 4/10 为否认型）；d2factmid 0/10；对照 c7（同负载最后读）10/10 |
| P6-5 | **分页窗回喂：提取有效当且仅当窗口携带身份上下文**；截断标记下无误报完成。v1（窗口含事实但不含文件标题，事实句又无主体名）answer 0/10 且决策继续读下一文件；v2 修正（头部窗口含标题+事实）恢复 8/10（750-token 窗），但 1500-token 窗反而 3/10（更大窗口未受益）；出窗条件 0/10 携带且模型正确继续读（无误报完成） | v2：f1 8/10、f3 3/10、f2/f4 0/10；decision 全部 read_file 继续 |
| P6-6 | **大文件回喂下答案阶段指令被系统性违反**（P2-3 在高负载的放大）：answer 格（"tools are now unavailable"）在 7.5k 多文件与分页窗条件下大量输出工具调用（v1 e 条件 40/40）；单文件低负载则基本遵守。负载越大，收尾纪律越差——与第二轮"单文件 4.7k–5k 悬崖是工作流纪律先崩"一致 | v1 e1-e4 decision/answer：answer 格全部输出 read_file 等调用；c1-c3 单文件低负载 answer 格未观察到违例 |
| P6-7 | **读取回喂带行号前缀（"N: "）无可测收益，且不缓解遗忘**：带/不带行号 × 事实位置全因子对照，factlast 携带 8/10（带）vs 10/10（不带）、factfirst 5/10 vs 6/10——差异全在噪声带；40 个 answer/decision 输出**零行地址引用**（无一处 report-N:NN 或 line N）；行号前缀实测 token 开销 +6.5%。"行号给内容一个稳定地址"的假设不成立（read 回喂场景；search_text 结果中的行号无副作用） | g1 8/10·no_tool 6/10；g3 10/10·3/10；g2 5/10；g4 6/10；linecite 0/40 |
| P6-8 | **编排对照：一条结构化检索命中入历史即可全面改变下游行为**。强制臂（模拟 search_text 命中入历史）：先检索后精读（命中+精读命中文件）decision no_tool **10/10**、carry 10/10——全 P6 最佳收尾形态；检索即答（仅命中行）decision 仍要精读（read_file 10/10）但 answer carry **10/10**（命中行文本本身足以作答，精读对正确性是多余的）；直接整读（同窗 c7 复刻）no_tool 5/10、carry 10/10。与 P6-1 交互：模型从不自发检索，但历史里有一条显式出处指针后收尾/携带全面改善——harness 引导一条命中进 transcript 的杠杆大于任何回喂格式改动。注：命中查询为脚本注入（事实句的字面子串），模型自发查询的命中质量仍未测（自发率 0 使其不可自然观测） | h1 no_tool 10/10·carry 10/10；h2 read_file 10/10·carry 10/10；h3 no_tool 5/10·carry 10/10 |

P6 对 Harness 的可执行含义：12. 检索修复的正确靶子是「决策端充分性判断 +
跨轮遗忘」，不是工具形态或分页（P6-2/P6-4）；13. 若引入分页读，窗口必须
内嵌文件身份（路径/标题行），否则事实无法归属（P6-5）；14. 顺序回喂的近因
偏差（P4-1）在文件读取域同样成立，多条回喂需要答案阶段的显式复述机制
（P6-4）。round-3 只出结论与方案，未做修复 A/B。
15. **读取回喂不必加行号**（P6-7：+6.5% token、0 引用、无收益）；**杠杆在
    引导一条结构化检索命中进 transcript**（P6-8：命中+精读 = no_tool 10/10，
    优于任何整读条件），harness 侧可考虑工具描述引导或首个读取前的自动
    检索（未验证——本轮未做修复 A/B）。
