# Harness 第二轮报告：量尺重建与重判（2026-08-31）

分支 `feat/harness-round2`（自 `feat/harness-preference-rebuild` 切出，两轮 diff
独立可 review）。本轮目标**不是继续加功能**，而是先修量尺（第一轮的 4 道 e2e
全是地板/天花板，测不出中等幅度改进），再用修好的尺子重判第一轮改动。

- 模型/端点/贪心采样同第一轮；`--api-stop-tokens none` 为必需（text 模式在该
  服务端稳定触发 HTTP 500 "empty response"，第一轮 e2e 的实际配置即 none）
- 实验通道：`rwkv-cli agent-eval` custom `--cases`（产品 markdown + 深锚点 +
  语义 no_tool + progressive router + max-steps 6），校准与所有 A/B 均为每题
  5 次独立运行；题目集与校准数据在 `test/e2e-calibrated/`
- 已知环境常量：贪心输出约 5% 不稳定，且为**批组成依赖**（同一 prompt 在不同
  批组成下输出可漂移）；所有 ±1 格的结论都按噪声对待，关键结论要求跨运行复现

---

## 一、题集校准记录（本轮最重要资产）

完整记录见 [`test/e2e-calibrated/CALIBRATION.md`](../../test/e2e-calibrated/CALIBRATION.md)。
方法：三类失败各造一批候选（难度围绕已知失败模式铺开），每题用当时二进制跑
5 次，只保留 1/5–4/5；冻结规则先于实验数据固定（类内按 (通过数,id) 交替分入
调优/留出）。

| 类 | 造题 | 保留 1/5-4/5 | 0/5 | 5/5 | 调优集 | 留出集 |
| --- | --- | --- | --- | --- | --- | --- |
| class1 长提取 | 25 | 4 | 10 | 11 | 2 | 2 |
| class2 双来源冲突 | 15 | 7 | 5 | 3 | 4 | 3 |
| class3 子 Agent 冲突 | 15 | 见下 | 多 | 0 | 见下 | 见下 |

### class3 的校准走了三轮（fixture 工程问题，如实记录）

1. **第一轮（连字符键）**：fixture 用 `bramblewick-register` 这类连字符键匹配
   子任务文本。实测模型把子任务写成泛化的 `"independent subtask"` 或
   `"research_official_register"`，键不命中 → 全部落到 fixture 兜底条目 →
   所有子 Agent 返回同一（错误）值，"冲突"根本不存在。该轮数据全部作废
   （`calibration/results-class3-contaminated.jsonl` 保留）。**教训：eval 的
   fixture 匹配必须按模型实际的子任务措辞设计，而不是按提示词里的措辞。**
2. **第二轮（match_all 主题+来源）**：要求子任务同时含主题与来源短语。模型
   的简短子任务字符串丢弃主题 → 兜底。再次作废。
3. **第三轮（每题独立 fixture 文件）**：eval 每次 invocation 只跑一题，改用
   每题专属 fixture（匹配裸来源短语 `official register` / `community wiki` /
   `news archive`，大小写/下划线归一化），兜底也是本题自己的条目——污染在
   结构上不可能。此轮数据有效。

有效 class3 校准（第三轮）结果与保留情况在本报告"第四/五步"引用处给出最终
数字；`CALIBRATION.md` 在 class3 定稿后同步更新。

### 结构性发现（与第一轮结论对照）

- **单文件长提取到 4k token 仍 11/11 通过、4.5k 开始掉到 4/5、5k 全灭
  （0/5，复现第一轮 e2e-long-extract-5k）**：单文件提取的悬崖在 4.5k–5k
  token 之间，比 P1-1 的格式降解点（10k–20k）窄得多——先崩的是"读回长文件
  后收尾作答"的工作流纪律，不是格式。
- **多文件提取（2×2k、3×1k）全灭 0/5**：失败形态 `list_files → read_file →
  search_text → read_file → …` 直到步数耗尽或答案阶段违例。第一轮"工具循环
  自终止是最大短板"的结论在题集层复现。
- **双来源冲突**：无纠正指令的裸问法（"这是什么数值？"）在文件与 web 两形态
  都能落在 1–4/5 的中带；显式"比对并判断哪个是权威"反而把 web 形态打到 0/5
  （模型在比对提示下改走再抓取循环）。
- **fetch 压缩触发带（>4k 估算 token 的单页）的题全部 0/5**：这正是 P5-2
  预言的整页回喂失败人群，预登记为第二步压缩 A/B 的诊断集（机制目标人群，
  非事后挑选）。

---

## 二、压缩的端到端结论（第二步：--compress-fetch 开/关对照）

第一轮 E5（query-aware 摘抄压缩）只有探针证据，因为 `--compress-fetch` 对评测
runner 实际无效（旗标只接了交互式 agent；本轮修复接线，见"代码改动"）。

**对照 1：诊断集（5 道长 web 页提取题，4k–6k token，压缩钩子唯一触发人群）**

| 题目 | 压缩 OFF（=校准基线） | 压缩 ON |
| --- | --- | --- |
| c1-web-4k | 0/5 | 5/5 |
| c1-web-4k5 | 0/5 | 5/5 |
| c1-web-5k | 0/5 | 5/5 |
| c1-web-5k-prose | 0/5 | 5/5 |
| c1-web-6k-fact80 | 0/5 | 5/5 |
| **合计** | **0/25** | **25/25** |

与 P5-2 探针结论**一致且幅度更大**：整页回喂时模型不在页内检索、转为再抓取
循环（0/25）；压缩页回喂后全部通过。抽查 trace 确认钩子真实触发（feedback
从 ~25k 字符缩到几字节摘抄）。

**对照 2：冻结调优集 8 题（页长低于阈值，压缩不应触发——中性检验）**

| 题目 | OFF | ON |
| --- | --- | --- |
| c1-file-2k-deep80 | 4/5 | 5/5 |
| c1-files-2x1k5-named | 4/5 | 4/5 |
| c2-files-plain-1k | 3/5 | 5/5 |
| c2-files-prior-2k | 4/5 | 5/5 |
| c2-web-official-last-1k | 4/5 | 5/5 |
| c2-web-prior-soft-2k | 1/5 | 0/5 |
| c3-three-correct-middle | 1/5 | 0/5 |
| c3-two-official-first-verify | 1/5 | 0/5 |

低于阈值的题压缩在机制上是 no-op；观察到 +7/−3 的漂移全部落在 ±1 格内，与
批组成噪声一致（c3 两题与压缩无任何交互路径，也出现了 −1，佐证这是环境噪声
而非压缩效应）。**结论：压缩 ON 在不触发带无行为变化（机制 no-op），在触发带
0/25 → 25/25。**

**决策：`--compress-fetch` 从实验开关改为默认开启**（显式 `--compress-fetch=false`
保留作 A/B 通道）。依据：0/25→25/25 的触发带效应 + 不触发带中性 + P5/P5-ZH
探针链完整。中文页的例外见第三步。

---

## 三、中文长页压缩结论（第三步，探针层）

完整数据在 `test/probes/p5-zh-compression/`（真实 zh.wikipedia 文本，28 篇，
World 词表实测 5k/10k token 页，60% 深度埋点，10 实例/格，4 轮提示词迭代）。
PREFERENCES.md 已按格式追加 P5-ZH-1..4。摘要：

| 形态（均 +fast-think） | 阶段 A 保留率（5k/10k） | 阶段 B 数值进入（5k/10k） |
| --- | --- | --- |
| 现行 harness 英文 extract 指令 | **2/10 · 2/10** | 2/10 · 1/10 |
| extract 中文改写（3 轮迭代） | ≤5/10 · ≤3/10 | — |
| bullets-zh | 6/10 · 2/10 | — |
| quote-zh（单句） | 8/10 · 2/10 | 7/10 · 1/10 |
| summary-zh（无约束） | 9/10 · 7/10 | 4/10 · 1/10 |
| **clean-summary-zh（内容锁定）** | **10/10 · 9/10** | **6/10 · 6/10** |
| 决定性对照：埋点句原文直接喂回 | — | **10/10 · 10/10（0 再搜索）** |
| 整页对照 | — | 0/10 · 0/10 |

结论：

1. **P5-1 的形态排序在中文上翻转**。extract 在中文触发逐字复读循环（P1-3
   同机制）：同一句原样重复抄到 256 token 预算耗尽，60% 深度的埋点句从未被
   摘到——现行 harness 指令对中文页无效且有害。
2. 内容锁定摘要（≤3 句、只用原文词句、禁任务回声）把保留率恢复到英文水平
   （10/10·9/10），但阶段 B 只有 6/10·6/10——残余失败是部分输出仍带"根据您
   提供的文本"类回声，决策模型将其视为非页面内容而再次搜索。
3. 埋点句原文喂回 20/20 证明**中文决策阶段本身无问题**；差距全部在压缩输出
   的可用形态上。中文页的端到端收益预期系统性低于英文页。
4. 方法修正（P5-ZH-4）：数值计数必须做千分位/全角归一化（模型英文作答时写
   "6,412"，原始子串检查漏判）。

**对默认开启决策的边界**：压缩默认开启覆盖英文页；中文页需要按语言切换压缩
指令（内容锁定摘要），在指令切换落地前，中文长页不在压缩收益范围内（fail-open
保证不劣于现状，但浪费一次压缩调用）。

---

## 四、no_tool 证据门控（第四步）

三种框架层方案全部实现并默认关闭（`--no-tool-gate state|evidence`、
`--answer-stage-lead N`，见第六节）：

- **state**：首次成功工具调用前，目录不提供 no_tool、发出的 no_tool 一律驳回
  （"还没有工具成功运行过"）；首次成功调用后目录重新挂载 no_tool。
- **evidence**：no_tool 的 reason 必须以 10 字符归一化（大小写/标点/空白折叠，
  保留 CJK）shingle 命中本回合真实 Function output 载荷，否则驳回并要求重试。
- **lead（答案阶段强制前移）**：步数预算结束前 1 步强制进入答案阶段，且答案
  阶段的工具违例获得一次不占用协议重试预算的专项重问。

**对照 1：冻结调优集 8 题（三门 vs 基线，各 5 次）**

| 题目 | 基线 | state | evidence | lead |
| --- | --- | --- | --- | --- |
| c1-file-2k-deep80 | 4/5 | 5/5 | 5/5 | 5/5 |
| c1-files-2x1k5-named | 4/5 | 5/5 | 5/5 | 5/5 |
| c2-files-plain-1k | 3/5 | 5/5 | 5/5 | 5/5 |
| c2-files-prior-2k | 4/5 | 5/5 | 5/5 | 5/5 |
| c2-web-official-last-1k | 4/5 | 5/5 | 5/5 | 5/5 |
| c2-web-prior-soft-2k | 1/5 | 0/5 | 0/5 | 0/5 |
| c3-three-correct-middle* | 1/5 | 0/5 | — | — |
| c3-two-official-first-verify* | 1/5 | 0/5 | — | — |
| **合计** | 20/30 | 25/30 | 25/30 | 25/30 |

（*class3 行的 state 臂跑在 fixture 修复前，数字已作废；evidence/lead 未跑
class3 调优集。）

三个**机制完全不同**的门控给出逐格相同的结果（+5/−1 复制三份）——这不是门控
的效应，而是公共因素（重建的二进制 + 运行时间窗）叠加批组成噪声。无法归因给
任何一种门控。

**对照 2：循环地板诊断集 5 题（门控的真正靶区，各 5 次）**

| 题目 | 基线 | state | evidence | lead |
| --- | --- | --- | --- | --- |
| c1-files-2x1k-unnamed | 0/5 | 0/5 | 0/5 | 0/5 |
| c1-files-2x2k-named | 0/5 | 0/5 | 0/5 | 0/5 |
| c1-files-3x1k-unnamed | 0/5 | 0/5 | 0/5 | 0/5 |
| c1-web-3k | 0/5 | 0/5 | 0/5 | 0/5 |
| c1-web-5k | 0/5 | 0/5 | 0/5 | 0/5 |
| **合计** | **0/25** | 0/25 | 0/25 | 0/25 |

失败形态分析：这些题的失败不是"不收尾"，而是"没收找到"——模型循环重读直到
步数耗尽；lead 臂确实消除了答案阶段硬违例（失败从 protocol_invalid 变为
步数耗尽前的空 no_tool），但分数不变：**模型答不出它没找到的东西**。

**结论（第四步）：三种门控在调优集上不可与噪声区分，在循环地板上零效果；
门控瞄准的失败模式（无证据谎报完成）在本题集族中不存在——本题集的约束是
检索纪律与近因偏差，不是终止机制。三种方案均不合并到默认路径（代码保留为
实验旗标）。E6-2/E6-3 的两难在 e2e 层仍未解决，且数据说明它不是端到端分数
的主要杠杆。**

---

## 五、第一轮改动的重判（第五步）

### E2 子 Agent 块状回喂（false_hit 主指标）

类3 题集经 fixture 修复后（每题独立 fixture，兜底污染结构性排除），块状回喂
（现行）vs 原始 JSON 回喂（`--subagent-raw-feedback`，E2 前的旧形态）各 15 题
× 5 次：

| 臂 | 通过 | false_hit（严格口径：错误值出现且正确值未出现） |
| --- | --- | --- |
| 块状回喂（现行） | 16/75 | 52/75 |
| 原始 JSON（E2 前） | 14/75 | 55/75 |

**结论：块状回喂在 e2e 层的优势（+2 通过、−3 false_hit）在批组成噪声内，
不构成可确认的端到端改善。** 与第一轮探针结论（old-json 11/20 → new-blocks
14-16/20、false_hit 9 → 3-4）的差异出在：探针是受控的两来源定序结构，e2e 题
目里模型自己撰写子任务、委派顺序可变，且多数题目叠加了错误先验——近因偏差
在 e2e 的表达比探针更杂。**处置：保留块状回喂**（探针层证据仍是正面的，且
形态更可读），但第一轮"端到端兑现"的说法撤回——e2e 层未验证有效。真正的
e2e 结构性复现是 P4-1 本身：official-first 0/5（fh=5/5）vs official-last
4/5，与探针的 −60pp 近因效应方向一致。

### E1 fetch token 预算

- **英文 e2e 上 E1 不可测**：旧 32k rune 上限对 ASCII 纯文本的切片点
  （32k chars ≈ 8k token）与 8k token 预算几乎重合——两者在英文题集上产生
  相同的截断，这是 E1 的设计使然（英文安全区间一致）。
- **中文 10k token 页诊断题（c1-zh-web-10k）**：8k 预算 0/5；旧上限仿真
  （35200 token，整页放行）0/5。10k 中文页不压缩时两种预算都过不了（P5-2
  检索失败主导），预算差异在 10k 档不改变结局。
- **处置：保留 E1（8k token 预算）**，依据仍是 P1-1 探针（10k 起降解、
  20k 崩溃）与中文页约 32k token 的旧上限暴露；e2e 层无法给出额外支持，
  如实记录。

### 其它第一轮改动

- web_search 块渲染 bug（本轮修复，见第六节）说明第一轮 E2 的渲染路径改动
  引入了 web_search 回喂回归——在第一轮的通道里不可见（eval 没接 web 工具），
  本轮 fixture 接线后才暴露。
- 深锚点放宽（routerless 决策武装）：调优集/诊断集全部运行都在该配置下，
  无独立 A/B（保持第一轮结论，不重判）。

---

## 六点五、HIG 收尾（第六步，可选任务）

**已实施：侧栏会话菜单按位置翻转弹出方向**（`App.tsx` Sidebar）：打开菜单时
测量按钮相对列表视口（最近的 `section` 滚动容器）的剩余下缘空间，<132px
（菜单约高 128px）时改为向上弹出（`bottom-[30px]`），末行菜单不再被视口
下缘裁剪。无新依赖、无设计 token/配色变化；前端 52/52 通过。

**方案（未实施）：顶栏 36px 触控目标**。现状：`--header-h` 内标签按钮视觉
高度 36px（`h-9`），运行配置按钮 28px，侧栏开关 32px；桌面指针优先场景可
接受，低于 HIG 的 44px 触控目标。三个方案：

1. **不可见命中区扩展（推荐）**：标签按钮加 `py` 内边距 + 等量负 margin
   （或 `::before` 命中层）把可点高度扩到 ≥44px，视觉零变化、布局零位移、
   不动设计 token；运行配置按钮同理。改动面 1 个文件 2 处。
2. 提高 `--header-h` 到 48px 并等比放大标签与按钮——视觉密度变化全局可见，
   需要产品决策。
3. 维持现状并文档化"桌面指针优先"决策——零成本，但触屏场景欠账仍在。

未实施（本轮只出方案）：需要产品在密度与触控之间做取舍。

## 六、代码改动清单（按文件，全部带依据）

| 文件 | 改动 | 依据 |
| --- | --- | --- |
| `internal/agent/eval/webfixture.go`（新增） | fixture 版 web_search/web_fetch（关键词/URL 子串匹配，确定性，无网络） | 任务第二步；E5 端到端验证通道缺失 |
| `cmd/rwkv-cli/main.go` | `--web-fixture`、`--compress-fetch`（eval 侧注册）、`--fetch-budget-tokens`、`--subagent-raw-feedback`、`--no-tool-gate state\|evidence`、`--answer-stage-lead` | 同上；第四/五步 A/B 通道 |
| `internal/agent/eval/runner.go`、`types.go` | eval 接线 fixture web 工具与预算覆盖；manifest 记录 compress_fetch/web_fixture/subagent_fixture | run.json 自描述，A/B 可复核 |
| `internal/agent/g1i_functions_transcript.go` | **修复：FormatToolResult 不再把 web_search 载荷送进子 Agent 块渲染**（任何带 `results` 数组的载荷都命中该路径，产品 markdown 协议下 web_search 的标题/URL/摘要全部丢失） | 接 fixture web 工具时实测发现；第一轮 E2 改动的回归 |
| `internal/agent/eval/runner.go`、`caseio.go` | 子 Agent fixture 支持 `match_all` 与大小写/连字符归一化；每题独立 fixture 文件（class3） | 校准三轮的教训（见第一节） |
| `internal/agent/runner_types.go`、`runner_turn.go`、`harness_profile.go` | no_tool 门控两方案（state：首次成功工具调用后才提供/接受 no_tool；evidence：reason 必须以 10 字符归一化 shingle 引用真实 Function output，否则驳回重试）+ answer-stage 前移与专项重问（`AnswerStageLead`） | 第四步，E6-2/E6-3 两难 |
| `internal/agent/g1i_functions.go`、`harness_profile.go` | `SubagentRawFeedback` 开关（块状回喂 vs 原始 JSON 回喂，仅作 E2 重判 A/B） | 第五步，false_hit 主指标 |
| `internal/agent/tools/web.go` | `FetchBudgetTokens` 覆盖（仅作 E1 重判 A/B；默认 8k 不变） | 第五步 |
| `cmd/rwkv-cli/main.go` | 移除 eval runCase 残留 DEBUG println | 清理 |
| `cmd/rwkv-app/frontend/src/App.tsx` | 侧栏会话菜单按位置翻转弹出方向（末行向上） | HIG：菜单不被视口裁剪 |
| `cmd/rwkv-cli/main.go` | `--compress-fetch` 默认 false → true（agent 与 agent-eval） | 第二步：0/25→25/25 触发带效应 + 不触发带中性 |

未合并/未采用：无新功能类改动（除实验通道本身）。

---

## 七、回归护栏

最终二进制（含 compress-fetch 默认开启与全部本轮改动）复跑两套护栏套件
（`test/round2/`）：

| 套件 | 本轮 | 第一轮基线 | 判定 |
| --- | --- | --- | --- |
| boundary（XML 协议） | **7/18** | 6/18（新旧二进制 5 次复跑的众数；7/18 是基线二进制的单次好抽样） | 不低于基线 ✓（answer 7/18、protocol 64/66、required 22/22） |
| bfcl-product（产品 markdown） | **24/60** | 24/60 | 持平 ✓（answer 42/60 = 70% 与基线 70% 一致；no_call 22/40 = 55% 与基线 55% 一致；route 52/80） |

compress-fetch 默认开启对两套套件均为 no-op（boundary 无 web 工具；
bfcl-product 无 web 工具），分数持平符合预期。

---

## 八、留出集最终跑分

留出集在全部实验定稿、默认配置（`--compress-fetch` 默认开启）落地后跑了一次
（每题 5 次），此前未做过任何针对性调参：

| 题目 | 校准基线 | 留出最终 | 类 |
| --- | --- | --- | --- |
| c1-file-4k5 | 4/5 | 5/5 | class1 |
| c1-web-2k | 4/5 | 5/5 | class1 |
| c2-files-prior-soft-2k | 2/5 | 5/5 | class2 |
| c2-web-official-first-1k | 3/5 | 5/5 | class2 |
| c2-web-official-first-15k2 | 4/5 | 5/5 | class2 |
| c3-three-majority-correct | 4/5 | 3/5 | class3 |
| c3-two-official-first-verify | 1/5 | 0/5 | class3 |
| **合计** | 22/35 | **28/35** | |

**解读（重要的方法论发现）**：留出集**高于**调优集基线（28/35 = 80% 对
22/35 = 63%），方向与过拟合相反。c1/c2 五题全部升到天花板，class3 两题各降
1 格。留出运行与校准相隔数小时、服务端负载与批组成不同；结合本轮反复观察到的
"批组成依赖的贪心漂移"（同一题在不同时间窗的通过数可整体移动 ±1–3 格，见
第四节三门控同格复制现象），**跨时间窗的通过率漂移大于调优/留出的划分差**。

含义：1/5–4/5 的"中带"不是题目的稳定属性，而是题目×时间窗的属性。本轮所有
**同窗口内**的 A/B（压缩开关、门控、E2 两臂）仍有效——配对双方同窗运行；
但**跨窗**比较（如校准基线 vs 留出、或与第一轮任何数字直接对比）不可用于
效应量判断。后续轮次若继续用校准题集，A/B 两臂必须同窗交错运行，或定期用
锚点题重校窗口漂移。

---

## 九、遗留问题和建议

1. **fetch 压缩的中文指令切换未落地**：P5-ZH 证明现行英文 extract 指令对
   中文页无效（复读循环），调优出的"内容锁定摘要"形态（保留率 10/10·9/10、
   阶段 B 6/10·6/10）尚未接进 `runner_compression.go`（按页语言切换提示词
   属于新功能，本轮按约定未做）。默认开启的 compress-fetch 对中文页是
   fail-open：浪费一次压缩调用后回退整页，不劣于现状。
2. **工具循环自终止仍未解决，且被证明不是分数杠杆**：第四步显示终止机制
   （三门控）改不动循环地板——模型答不出没找到的东西。杠杆在检索纪律
   （分页读、行级定位、检索式读取），建议下一轮探针测"多文件/长文件的
   定向读取"偏好，而不是继续改收尾机制。
3. **近因偏差（P3-2/P4-1）在 e2e 复现且未被任何 harness 手段缓解**：块状
   回喂在 e2e 与原始 JSON 打平。可试方向：把可信来源显式排最后（harness
   通常无法预知可信度，实用价值存疑）、或答案阶段对"数值来源"做结构化
   强制复述。
4. **批组成依赖的贪心漂移是量尺的最大噪声源**（约 ±1 格/题/窗）：后续所有
   小样本结论都必须同窗配对采集；"5% 不稳定"的描述应升级为"批组成依赖、
   时间窗漂移"。
5. **`--answer-stage-lead` 与 `--no-tool-gate` 保留为实验旗标**（默认关），
   代码路径有门控事件记录（`gate_events`），后续可复用。
6. **E2 探针结论与 e2e 结论的落差**提示：探针层 +2~+5 格的效应在端到端
   （模型自撰子任务、多来源、错误先验混合）会被稀释到噪声内。下一轮的
   探针设计应直接在 e2e 通道做（fixture 化），避免两层结论脱节。
7. 顶栏 44px 触控目标方案已给出（见六点五节），待产品决策。
8. bfcl-product 的 no_call_accuracy 55% 未动（同第一轮遗留）。

## 引用索引

## 引用索引

- 题集与校准：`test/e2e-calibrated/`（candidates/、calibration/ 含各 A/B 臂、frozen/、CALIBRATION.md）
- 回归护栏复跑：`test/round2/`（boundary-final、bfcl-product-final）
- 中文压缩：`test/probes/p5-zh-compression/`（out/p5zh-stage-a{,2,3,4}、stage-b{,2,-factonly}、counts.json）
- 偏好原始结论：仓库根 `PREFERENCES.md`（P5-ZH 节）
