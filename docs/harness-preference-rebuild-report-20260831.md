# Harness 偏好重建报告（2026-08-31）

分支 `feat/harness-preference-rebuild`（与 main 同起点 1f912cb，全部工作在分支上）。
本轮方法：**先用高并发 API 测出模型自身的输出偏好，再围绕偏好重建 Harness**；
没有实验结论支撑的改动一律不进代码。逐条偏好的完整数据在仓库根
[`PREFERENCES.md`](../../PREFERENCES.md)；全部原始输出、分类与计数保留在
`test/` 下并已提交。

- 模型：`rwkv7-g1i-7.2b-20260805-ctx16384`
- 端点：`api-7b.rwkvos.com`（rwkv_lightning_cuda，`/v1/batch/completions`，贪心
  temperature 0.001 / top_k 1 / top_p 1 / penalty 归零，CF Access 认证）
- 探针框架约定沿用 `rwkv-abstention-lab` 与 `RWKV-Toolcall-Bench`（同一后端
  客户端形状、JSONL 落盘、事后分类、x/n 计数），未另起框架
- 已知后端问题：贪心下约 5% 输出不稳定；所有意外结果均以完整重跑确认

---

## 一、模型偏好结论（PREFERENCES.md 成文摘要）

每条格式：结论 + x/n（两次独立运行分别给出，run1 / run2）+ 实验目录。

### 长上下文（P1，test/probes/p1-long-context/）

400 格（2 锚点 × 5 长度 × 4 正文类型 × 10 实例），全量跑两遍，逐格分类
一致率 345/400 = 86.2%，分歧集中在 10k/20k 边缘格，条目级结论复现。

| 编号 | 结论 | 数据（run1 / run2） |
| --- | --- | --- |
| P1-1 | 深锚点（` ```json + {"name":"`）决策格式合规到 10k token 基本无损，20k 明显降解 | call_ok：500/2k/5k = 40/40 · 40/40；10k = 37/40 · 40/40；20k = 30/40 · 32/40 |
| P1-2 | 无锚点续写从 2k 开始降解，5k–10k 崩溃 | 500 = 39/39·39/40；2k = 35/40·35/40；5k = 29/40·25/40；10k = 16/40·20/40；20k = 20/40·23/40 |
| P1-3 | 复读从 10k 档出现，自我复读为主、正文复读并存 | deep：10k = 2/40，20k = 7/40；bare：10k = 8/40，20k = 10/40；500–5k（deep）0/120 |
| P1-4 | 含代码块正文对**无锚点**续写最毒（围栏打架成立）；对深锚点不构成主要威胁 | bare+code：5k = 0/10·0/10，10k = 0/10·0/10，2k = 5/10·5/10；deep+code：10k = 7/10·10/10 |
| P1-5 | 正文内容污染输出罕见（哨兵检测） | deep 两次运行 0 污染；bare 零星 4/400 |
| P1-6 | 模型从不主动弃权；退化时产出坏格式而非 no_tool | no_tool 选择次数在全部 400 格中为 0 |
| P1-7 | 无锚点时自发 `<think>` 且随长度增加；深锚点下为 0 | bare：500 = 2/40 → 10k = 30/40；deep：0/200（两跑） |

### 工具结果回填（P2，test/probes/p2-tool-result-feedback/）

| 编号 | 结论 | 数据 |
| --- | --- | --- |
| P2-1 | 短结果下五种回填包裹全部无差异——包裹格式不是杠杆 | decision 各 20/20；answer = 20/20·19/20·20/20·20/20·20/20（合计 99/100） |
| P2-2 | 长结果下 plain 与 JSON 包裹降解速度相同 | 5k/10k × 2 跑 = 全部 10/10（合计 40/40） |
| P2-3 | 工具链未闭合时 answer 阶段模型拒绝作答、坚持先调工具 | 100 条 answer 里 94 条输出 calculator 调用而非回答 |

### 多来源冲突（P3，test/probes/p3-multi-source/）

16 条件全因子 × 20 实例 × 2 跑，条件级结论逐格复现。

| 编号 | 结论 | 数据 |
| --- | --- | --- |
| P3-1 | **"只信第一个"不成立**：结构化并列下位置效应为 0 | structured：correct_first vs correct_last = 19/20 vs 19/20（0 pp），多次复现 |
| P3-2 | 顺序拼接下存在轻度**近因**效应（更信最后一条） | sequential：correct_first 17/20·17/20，correct_last 20/20·20/20（−15 pp） |
| P3-3 | 预标注冲突与"要求比对"提示词均无可靠效果 | 开/关差 ≤1 格（n=20，噪声内） |

### 子 Agent 回填（P4，test/probes/p4-subagent-feedback/）

| 编号 | 结论 | 数据 |
| --- | --- | --- |
| P4-1 | 子 Agent 结果存在**强近因效应**：正确结果排首位时大面积采纳错误的第二条 | separate：correct_first 6/20·6/20，correct_last 18/20·18/20（−55~−60 pp）；batch：11/20 vs 15-16/20 |
| P4-2 | 框架层警示标注（"可能有误"）不能修复该偏差 | 加标注 correct_first 7/20·8/20（基线 6/20），n=20 噪声内 |
| P4-3 | 提示词要求比对同样无效 | 开/关逐格相同或差 ≤1 格 |
| P4-4 | 合并为单条回喂显著缓解（不能消除）近因偏差 | batch correct_first 11-12/20 vs separate 6-7/20 |
| P4-5 | 子 Agent 结果缺少"来源权威信号"时正确率上限明显更低 | P3 结构化 95-100% vs P4 batch 55-85%（唯一结构差异是逐条来源标签） |

### 长页压缩（P5，test/probes/p5-compression/）

| 编号 | 结论 | 数据 |
| --- | --- | --- |
| P5-1 | 逐句摘抄 + fast-think 预填是最优压缩形态 | 保留率 10/10·9/10（5k/10k），平均压缩长度 ~110 字符；raw 形态 3-4/10@10k |
| P5-2 | **整页喂回时模型不在页内检索答案，改为再抓取；压缩页喂回则正确作答** | 阶段 B 答案进入调用：extract+ft 9/10·8/10；**整页 1/10·0/10**（20 格中 11 次再 web_fetch、7 次改 web_search） |
| P5-3 | 压缩调用必须带 fast-think 预填（P1-7 同机制） | extract raw 5k = 4/10 vs extract+ft 10/10 |

### 文件工具工作流（E6，test/filetools-ab/，8 题 × 两形态 × 6 轮迭代）

| 编号 | 结论 | 数据 |
| --- | --- | --- |
| E6-1 | 两形态机制都可用；Form B（whole，2 工具）required-tool 完成率更高 | 最终轮 B 100% vs A 60%；历史轮 B 88.9-100% vs A 50-60% |
| E6-2 | **无 no_tool 出口时模型无法终止工具循环**（编辑成功后无限 read_file） | 去掉 no_tool：answer 0-12.5%，全部步数耗尽 |
| E6-3 | 有 no_tool 时模型用它谎报完成（不调工具即宣称已修改） | required 完成率跌至 0-60%；收紧描述后仅部分改善（53-64%） |
| E6-4 | 路由器需要编辑类 few-shot 示例，否则把编辑任务判为 respond | 加示例后 route 100% 正确 |
| E6-5 | 模型把可选整数发成 null；schema 需用 nullable + 默认值 | list_files 风格声明后该错误消失 |

---

## 二、Harness 改动清单（按文件，每条注明依据）

| 文件 | 改动 | 依据 |
| --- | --- | --- |
| `internal/agent/tools/web.go` | 删除 32k rune 上限，改为每调用 8k token 共享预算（按 URL 顺序分配，二分截断，标记 truncated） | P1-1（10k 起降解、20k 崩溃）；旧上限对中文页约等于放行 32k token |
| `internal/agent/runner_compression.go`（新增） | query-aware 摘抄压缩：页超过 4096 估算 token 时，用同一模型 + fast-think 预填执行"逐句摘抄"，回喂压缩版；原始 payload 保留在 `Step.ToolResult`，压缩副本在 `Step.ToolResultFeedback`；失败 fail-open | P5-1/2/3（整页 1/20 vs 压缩 17/20；压缩保留 19/20 仅在带预填时成立） |
| `internal/agent/runner_tool_step.go` | web_fetch 成功后、回喂前调用压缩钩子（`CompressFetch` 选项开启时） | 同上 |
| `internal/agent/runner_types.go` | `Options.CompressFetch`；`Step.ToolResultFeedback` | 同上 |
| `internal/agent/g1i_functions_transcript.go` | `FormatToolResult` 将 spawn_agents 的 raw JSON 渲染为逐条带来源标签的块（`--- Sub-agent N: <sources> --- / Task / Result`）；JSON wire 格式不变 | P4-1/P4-4/P3-1：raw JSON batch 11/20 → 块状 14-16/20（E2 验证 `test/probes/p4-subagent-feedback/out/e2-verify2/`） |
| `internal/agent/runner_turn.go` | 产品 profile 的决策锚点不再依赖路由器存在：非 respond 路由一律武装（DecisionFakeThink 模式除外；XML 协议保持原路由门控） | P1-1 vs P1-2：无锚点决策从 2k token 起降解 |
| `internal/agent/route.go` | workspace bundle 为可编辑（`Editable`）时，路由 few-shot 增加两条编辑示例 | E6-4：路由器把编辑任务判为 respond |
| `internal/agent/tool_registry.go` | `ToolBundle.Editable`；新增 `PermissionWorkspaceWrite` | E6-4 |
| `internal/agent/tools/fileedit.go`（新增） | 文件编辑工具两种形态：Form A lines（read_lines/write_file/replace_lines/append_file）与 Form B whole（read_lines/write_file）；工作区 containment、分页读上限 200 行、可空行号默认值 | E6-1/5；任务指定"不要 str_replace"（old_str 死循环风险） |
| `internal/agent/g1i_functions.go` | 提供写工具时收紧 no_tool 描述（禁止谎报文件操作） | E6-3（部分有效；完整解决见遗留） |
| `internal/agent/harness_profile.go`、`api/session.go`、`api/types.go`、`cmd/rwkv-cli/main.go` | `--compress-fetch` / `--file-tools lines|whole` 旗标与 App 配置面贯通；custom `--cases` 现在尊重 `--agent-protocol markdown`（此前被静默忽略，E6 期间发现并修正；内建套件保持原映射） | 使实验可从 CLI 复现 |
| `internal/agent/testdata/golden_prompt/{product_submit_fence_prefix,product_fenced_tool_then_answer}.txt` | re-lock：routerless 产品决策现在也武装围栏锚点 | P1-2；仓库政策要求 golden 随协议变更重锁 |

未采用（有数据支撑的"不作为"）：不添加"来源冲突请比对"类提示词（P3-3）、
不添加子 Agent 警示标注（P4-2）、不更换回填包裹格式（P2-1/2）。

---

## 三、实验记录（含无效实验）

每条：现象 → 改法 → 对照数据（全部轮次）→ 结论 → 合并或回滚。

### E1 fetch 切片按 token 预算 — 合并

- 现象：32k rune 上限对英文约 6k token（安全）但对中文约 32k token（远超
  P1-1 降解点）；P1 显示 20k 注入时格式合规仅 30-32/40。
- 改法：8k token 共享预算 + 校准估算器（ASCII/4.0 + CJK×1.1，实测正文
  3.85-5.42 chars/token，向高估方向偏置）。
- 对照：预检中本地估算器与服务端 `/v1/tokens/count` 一致性 5/5；估算误差
  对 lists 型 -4%、prose 型 +29%（全部落在安全方向）。
- 结论：切片阈值从"字符"换成"token"且留出控制提示词余量。合并。

### E2 子 Agent 结果块状回喂 — 合并

- 现象：P4 强近因效应（-55~-60pp）；raw JSON batch 下 correct_first 仅 11/20。
- 改法：`--- Sub-agent N: <sources> ---` 块状单条回喂（新渲染）。
- 对照（`out/e2-verify` + `out/e2-verify2`，各 2 rendering × 2 positions ×
  20 实例 × 2 轮）：old-json 11/20·15/20（两轮一致）；new-blocks 14/20·16/20
  （两轮一致）；new-blocks-header 15/20·16/20。false_hit：old 9/5 → new 3-4/2-3。
- 结论：块状回喂 +2~+3 格，方向稳定但幅度小于 P3 场景（子 Agent 结果天然
  缺权威信号，P4-5）；取两变体中更简且略优的 header 形态合并。**未消除**近因
  偏差，这是模型上限。

### E5 query-aware 压缩 — 合并（默认关闭，`--compress-fetch` 显式开启）

- 现象：P5-2 整页喂回 1/20 正确且 18/20 转向再抓取/搜索；压缩后 17/20 正确。
- 改法：runner 内压缩钩子 + extract 提示词 + fast-think 预填 + 4096 token 阈值
  （P5 显示 5k 已发生检索失败，低于 P1 的 10k 格式降解点，故阈值取 4k）。
- 对照：P5 阶段 A/B 全量数据（见上表）；压缩前后原文均留轨迹。
- 结论：合并为实验开关；默认关闭是因为端到端评估通道（agent-eval）不接线
  web 工具，无法在 e2e 层验证（见"遗留"）。

### E6 文件工具 A/B — 合并工具实现；默认关闭；Form B 胜出

- 现象（6 轮迭代，全部 trace 保留）：
  1. custom 套件无路由器 → 决策无锚点 → `<think>` 漂移 → 0/8（P1-2 复现）；
  2. 修锚点后路由器把编辑任务判为 respond → 工具不可用；
  3. 加编辑示例后 no_tool 谎报完成 → required 0-60%；
  4. 去掉 no_tool → 无限 read_file 循环 → 步数耗尽（answer 0-12.5%）；
  5. `end_line` null → schema 改 nullable + 默认；
  6. 最终轮：Form B required 100% / Form A 60%。
- 改法：Form A/B 两套工具 + 路由示例 + 锚点放宽 + no_tool 描述收紧。
- 结论：**Form B（whole）胜出**（工具更少、完成率更高、replace_lines 无优势）；
  文件工具保持实验性门控（`--file-tools`）。阻塞项 E6-2/E6-3 是模型工作流纪律
  问题，不是形态问题——这本身就是本轮最重要的负结果之一。

### 回归护栏（boundary + bfcl-product）— 通过

- boundary：基线 7/18；重建二进制 6/18 · 6/18 · 6/18；**旧二进制复跑
  6/18 · 6/18**——6/18 是两版共享的众数，7/18 是单次好抽样；protocol 97.0% 与
  required 100% 完全一致（`test/baseline/main-boundary-20260831`,
  `rebuild-boundary-20260831{,-r2,-r3}`, `main-boundary-20260831-r{2,3}`）。
- bfcl-product：基线 24/60，重建 24/60；answer 70%=70%、route 65%=65%、
  protocol 85.6%≈85.3%、no_call 55%=55%（`rebuild-bfcl-product-20260831`）。
- 期间事故与修复：一次将 custom 的 markdown 分支错误套用到内建套件，boundary
  塌到 1/18（协议被翻转成 product markdown）；当轮定位并修复（分支仅对
  custom `--cases` 生效），随后按上述复跑证明无回归。

### 端到端验证（test/e2e/，4 题 × 5 次重复 × 新旧二进制）

- 新二进制（custom 套件 + 产品 markdown + 深锚点 + 路由器）：
  e2e-long-extract-5k 0/5、-10k 0/5、e2e-conflict-two-files 0/5、
  e2e-conflict-question-first 5/5。
- 旧二进制（custom 走 XML，即旧默认行为）：逐题 **完全相同**（0/5、0/5、
  0/5、5/5）。
- 结论：三类失败在端到端层由模型工作流纪律主导，本轮改动既不伤（回归双
  套件零变化）也不推不动的那部分；显式"两个来源都查一下"类提问（class 2
  带纠正指令）可达 5/5，与 P3-1/P3-2 的探针结论一致。class 3（spawn_agents）
  无法经 agent-eval 复现（runner 未接线 delegate 工具，见遗留），其证据由
  P4/E2 探针承担。

### 无效实验（明确记录）

1. **no_tool 描述收紧**（E6-3）：指令级修复只把 required 从 0-60% 提到
   53-64%，未达可用——与 P3-3/P4-2"指令级修复在本模型上偏弱"一致。保留代码
   （无害），问题靠门控默认关闭兜底。
2. **JSON 包裹回填**：P2-2 显示与 plain 无差异，不采用"换包裹"方案。
3. **冲突预标注 / 比对指令**（P3-3/P4-2）：无可靠效果，不写入 harness。
4. **Form A（lines）**：被 Form B 淘汰（E6-1 数据）。

---

## 四、App 改动清单

必修两处：

1. **会话侧栏三点菜单补齐**（`App.tsx` Sidebar、`ConfirmDialog`）：
   单一"删除"扩为 置顶/取消置顶 + 重命名 + 删除；新增
   `Backend.RenameConversation` / `Backend.SetConversationPinned`
   （`appservice.go`、`internal/appstorage/store.go`，绑定已用 wails3 beta.8
   再生成）；重命名走行内输入（Enter 提交 / Esc 取消），置顶会话带 Pin
   图标并排序置前（存储层 `PinnedAt` + Summary 排序）。**点击空白处/按 Esc
   自动收起菜单**（pointerdown + keydown 全局监听，菜单内部点击豁免）。
2. **轨迹时序/时长切换拨钮过渡动效**（`TraceToolbar.tsx`）：以测量的滑动
   指示条（transform + width，180ms cubic-bezier(.2,0,0,1)，
   motion-reduce 降级）替换生硬的瞬时底色切换，分段文字颜色 160ms 过渡。

自选打磨（3 处，均在 ≤5 限额内）：

3. **删除会话二次确认**：删除从静默执行改为 ConfirmDialog 确认（HIG：
   破坏性操作须可撤销或确认）。
4. **会话菜单可访问性**：`role="menu"/menuitem`、`aria-haspopup`、
   `aria-expanded`、按会话标题区分的 aria-label；菜单在键盘聚焦（focus-within）
   时也可见（原为纯 hover，`legacy.css`）。
5. **运行配置按钮 aria-haspopup/aria-expanded**。

HIG 过检记录——看到但未改的项（多为布局级或需产品决策）：

- 顶栏 tab 与按钮高度 36px，低于 44px 触控目标；桌面指针优先场景可接受，
  若要改涉及 header 布局（建议）。
- 侧栏菜单对最后一行可能溢出视口下缘，宜按行位置翻转弹出方向（建议，
  需测量逻辑）。
- 空会话列表仅有静态文案，可加空态引导插画/入口（建议，布局改动）。
- 触屏设备上 hover-only 的菜单可见性已由 focus-within 缓解，但移动端
  布局（sidebar scrim）整体未纳入本轮（建议另立移动端过检）。
- 主题切换按钮位于设置页内，主界面无快捷切换（产品决策，未改）。

前端测试 52/52 通过，Go 全部 25 包测试通过；未引入新依赖、未改设计
token/主题变量/配色、未替换组件库。

---

## 五、遗留问题和建议

1. **工具循环自终止是最大短板**（E6-2/E6-3、e2e 全部长提取题 0/5）：模型
   能正确调工具、能读回结果，但没有"收尾作答"的纪律；no_tool 又会被滥用于
   谎报。建议下一轮专门研究"证据门控的 no_tool"（要求 reason 引用既有
   Function output 的内容）或"答案阶段强制 + 工具调用软修复"的可行性。
2. **agent-eval 未接线 web/delegate 工具**：`--web`/`--subagents` 旗标对
   评测 runner 实际无效（工具装配在 `evalTools` 中缺失），压缩与子 Agent 的
   端到端验证只能经 App 或探针覆盖。建议给 eval 补 fixture 版 provider。
3. **压缩提示词仅覆盖英文合成页**：P5 的正文是英文合成文本；中文长页的
   保留率与压缩长度未测（估算器对 CJK 的偏置方向是安全的，但压缩效果未验证）。
4. **近因偏差未消除**（P3-2/P4-1）：合并回喂 + 来源标签缓解后仍存在；可尝试
   把可信来源显式排序到最后（harness 通常无法预知可信度，实用价值存疑）。
5. **`--file-tools` 建议保持关闭**直到 E6-2/E6-3 解决；Form B 实现已就绪。
6. **bfcl-product 的 no_call_accuracy 55%**（本轮未动）：与 P1-6"从不主动
   弃权"共同指向弃权判断薄弱，可作为下一轮偏好探针的输入。
7. 后端贪心 5% 不稳定是环境常量；本轮所有结论均以双跑/多跑确认，引用任何
   单次数字时请注明这一点。

## 引用索引

- 探针与数据：`test/probes/{p1-long-context,p2-tool-result-feedback,p3-multi-source,p4-subagent-feedback,p5-compression}/out/`
- 基线与回归：`test/baseline/`（main 与 rebuild 两代、多轮）
- 文件工具对照：`test/filetools-ab/`
- 端到端：`test/e2e/`
- 偏好原始结论：仓库根 `PREFERENCES.md`
- 框架约定来源：`/Users/no22/Projects/rwkv-abstention-lab`、`/Users/no22/Projects/RWKV-Toolcall-Bench`
