# 工具目录 agent-tool-v3：读写与网页工具重构 —— 实施规格书

> 2026-10-19 起草，给接手实现的编码 Agent 看。带"必须""不许"的句子是硬约束，后面都写了理由。
> **核心章节是 §2**：新工具的逐字描述、参数、返回样例、提示语原文，以及旧数据怎么迁移。这些只能照抄，不能自己发挥。
> **命名（2026-10-21 起）**：工具目录统一叫 `agent-tool-v主.次`。旧名 `work-v1/v2/v3` 对应 `agent-tool-v1.0/v2.0/v3`，规则见 §6。本文原名 `work-v3-tools.md`，正文里的 `work-v3-window` 这类 reason 值和 `docs/evaluations/work-v3-m0/` 目录名是历史数据，保持原样。

## 0. 目标

在**一次改动**里把读文件、改文件、网页三组工具重做，定为新目录 `agent-tool-v3`，App、评测、训练数据渲染三处共用同一份。三个要解决的问题，都有 10-17 新考卷的数据支撑（v2.1 lr2e-5，两遍）：

1. **大文件一读就是几万 token。**`read_file` 一次最多返回 64KB，不带行号，截断时只给 `"truncated": true`。一遍里有 59 次读取超过 4KB、14 次被截断（模型只能拿半个文件去计数）。读过大文件的题通过率 14–29%，其他题约 48%。
2. **两个读文件工具重复，其中一个没人用。**`read_lines`（带行号、分段、返回总行数）在考卷里每题都提供，但只被调用过 2 次；`read_file` 被调用了约 1080 次。`replace_lines` 的 30 次报错里有 21 次是"end_line 超过最后一行"——模型读文件时看不到行号，也不知道总行数。
3. **网页一抓就是 8K token，训练里却从没见过长网页。**`web_fetch` 每次调用共享 8K token 预算、只截断不保存。训练集里 web_fetch 结果最长 830 字符。上下文越长，模型越容易出错：决策步格式出错率在 2K 以下为 0.6%，16K 以上为 8–10%。

**最关键的取舍**：不走纯 bash（bash 是这个模型最容易出错的工具，约 40% 的调用报错或非零退出），也不让模型自己写摘要（10-19 实测 RWKV 自摘要会编造内容）。做法是**把长内容存成文件，上下文里只放开头、目录和文件路径**，后面用已经训练过的 `read_file`、`search_text` 按需去读。这就是 Manus 说的"可恢复压缩"。

## 1. 改动总览

| 工具 | agent-tool-v2.0 | agent-tool-v3 | 改动类型 |
|---|---|---|---|
| `read_file` | 整个文件原文，≤ 64KB，无行号 | 带行号、可指定行区间；默认一屏，超出时告诉模型总行数和下一步怎么做 | **重做**（吸收 read_lines） |
| `read_lines` | 行区间、带行号、≤ 200 行 | **删除** | 合并进 read_file |
| `list_files` | 路径、类型、大小 | 文本文件另加行数 `lines` | 加字段 |
| `replace_lines` | end_line 超过末行就报错 | end_line 超出时截到末行；返回改动处前后几行（带行号） | 放宽 + 加回显 |
| `write_file` / `append_file` | — | 拒绝"每行都带行号前缀"的内容 | 加护栏 |
| `search_text` | 搜整个工作区 | 默认不搜 `.web/`，path 以 `.web` 开头时才搜 | 加排除 |
| `web_fetch` | 截断到共享 8K token | 本地正文抽取；短页面原样返回；长页面存成 `.web/<n>-<host>.md`，只返回开头、目录和总行数 | **重做** |
| `web_search` | 描述里写死 "with Brave" | 描述去掉后端名 | 只改描述 |
| `calculator` | 不支持 sqrt 等 | 加 `sqrt pow ln log10 exp`；报错时提示怎么改 | 加函数 + 改报错 |
| `data_query` | 参数组合不对就报错 | `sum/avg/min/max` 只给 `field` 或 `expression` 之一时照常算；`count` 忽略多余的 field | 放宽 |
| `bash` `datetime` `get_weather` | — | 不变 | — |

agent-tool-v3 共 13 个工具（agent-tool-v2.0 是 14 个）。

**不做的事**（以下方案都考虑过，**不许**实现）：

- **纯 bash 目录。**原因见 §0。
- **web_fetch 加字符偏移参数**（MCP fetch 的 `start_index`、Claude Code WebFetch 的 `offset`）。10-19 做过一版，被用户否掉：模型要从结果里抄字符数，工具参数和训练数据对不上，缓存藏在工具里成了看不见的状态。
- **web_fetch 让模型或外部模型先摘要**（Claude Code、Gemini CLI 的 `prompt` 参数）。10-19 实测：RWKV 自摘要会编造；DeepSeek 摘要准确，但每次要调外部 API，评测也不再可复现。
- **str_replace 式编辑**（Claude Code Edit、Anthropic text editor、Gemini `replace`）。它要求模型把原文逐字抄出来，RWKV 是固定大小状态，逐字回忆远处的长段落正是它的弱项；而行号编辑只需要记住几个数字。等 agent-tool-v3 稳定后可以单独做 A/B，这一版不做。
- **删掉 data_query。**它约 31% 的调用报错，但归因后有 26 次是参数组合问题（比如 sum 同时给了或都没给 field/expression），放宽就能消掉，不是工具本身没用。
- **改 agent-tool-v2.0。**agent-tool-v2.0 的代码路径必须原样保留，见 §6.1。

## 2. 工具逐字规格（核心章节）

下面每个工具给出四样东西：进 `<tools>` 的 `description` 和 `arguments` 原文、`Parameters` 的 JSON Schema、返回 JSON 样例、提示语原文。

- `description` 和 `arguments` **必须逐字照抄**。它们进系统提示词，也进目录哈希（`workToolCatalogHash`）；改一个字，所有训练数据都要重新渲染。
- 提示语（`note`）用中文，沿用 10-16 空结果探针的结论：中文提示效果最好，英文"tell the user…"会被模型原样复述成终答。

### 2.1 read_file

```json
{"name":"read_file","description":"Read a UTF-8 text file in the workspace. Lines come numbered as \"N: text\". Without start_line/end_line it returns the first screen (up to 200 lines); the result says how many lines the file has.","arguments":{"path":"relative file path","start_line":"optional integer >= 1","end_line":"optional integer >= start_line"}}
```

Parameters（strict，三个键都列为 required，可选值用 null，和现在的 read_lines 一致——模型习惯给可选整数传 null）：

```json
{"type":"object","properties":{"path":{"type":"string","description":"Workspace-relative file path."},"start_line":{"type":["integer","null"],"minimum":1},"end_line":{"type":["integer","null"],"minimum":1}},"required":["path","start_line","end_line"],"additionalProperties":false}
```

**一屏的规则**（按顺序判断，哪个先到就停）：

1. 从 `start_line`（默认 1）开始，最多 200 行。给了 `end_line` 就以它为准，但 `end_line - start_line` 不得超过 199。
2. 累计字节数（不含行号前缀）超过 12KB 就在这一行之前停。第一行本身就超过 12KB 时至少返回这一行（见第 3 条）。
3. 单行超过 2000 个字符时截到 2000，行尾接 ` …[本行共 N 字符]`。

**为什么是 200 行 / 12KB**：200 和原 read_lines 的上限一致，训练集里已有的 35 次 read_lines 调用语义不变。12KB 大约是 3–4K token；训练集 read_file 结果的 p90 是 3.3KB，绝大多数现有轨迹不会被截。M0 会用真实分布复核这两个数，复核前不许改。

**整个文件都在一屏内**（最常见的情况）：

```json
{"path":"config/app.yaml","start_line":1,"end_line":3,"total_lines":3,"content":"1: name: billing\n2: port: 8443\n3: region: eu-west\n"}
```

**没读完**：

```json
{"path":"logs/gateway.log","start_line":1,"end_line":200,"total_lines":2431,"content":"1: 2026-09-15T00:00:03Z GET /health 200 3ms\n…\n200: 2026-09-15T00:41:17Z POST /v1/orders 201 88ms\n","note":"只显示了第 1–200 行，文件共 2431 行。往后读用 start_line=201；要查找或统计，用 search_text，或用 bash 的 grep、wc、awk 处理整个文件。"}
```

note 模板（`{a}` `{b}` `{total}` `{next}` 是占位符，其余逐字照抄）：

```
只显示了第 {a}–{b} 行，文件共 {total} 行。往后读用 start_line={next}；要查找或统计，用 search_text，或用 bash 的 grep、wc、awk 处理整个文件。
```

`b == total` 时不带 note。`start_line > total` 时返回 `content: ""`，note 为 `文件只有 {total} 行，第 {a} 行之后没有内容。`。

- **不许**再有 64KB 读取上限。行数、字节都按整个文件算——agent-tool-v2.0 的 read_lines 只读前 64KB 再数行，超过 64KB 的文件总行数会算错、后面的行也读不到，这是要修的 bug。整个文件大小上限改为 8MB；超过时报错 `文件超过 8MB，用 bash 的 head、grep、wc 处理。`
- 非 UTF-8、二进制文件的报错文字保持不变（考卷里有故意放的 GBK 文件）。

### 2.2 list_files

description 不变。每个条目加 `lines`：文本文件且 ≤ 8MB 时给出行数，否则不给这个键。

```json
{"entries":[{"path":"logs","type":"dir"},{"path":"logs/gateway.log","type":"file","size":214377,"lines":2431}],"truncated":false}
```

- 默认（path 为空或 `.`）**不列** `.web/`；path 以 `.web` 开头时照常列出。
- 要数行就得读整个文件：单次调用累计读取超过 32MB 后，后面的文件都不再给 `lines`。目的是不让 list_files 在大目录上变慢。

### 2.3 replace_lines

description 改成：

```json
{"name":"replace_lines","description":"Replace lines start..end (1-based, inclusive) of a workspace text file with the given content lines. Use the line numbers shown by read_file; do not include the \"N: \" prefixes in content. An end_line past the last line means through the last line.","arguments":{"path":"relative file path","start_line":"integer >= 1","end_line":"integer >= start_line","content":"replacement lines"}}
```

- `end_line > total` 时按 `total` 处理，不报错，返回值里加 `"end_line_clamped": true`。考卷里 30 次报错有 21 次就是这个。
- `start_line > total + 1` 仍然报错，报错文字为 `文件只有 {total} 行，start_line 最大是 {total+1}（在末尾追加）。`
- 返回改动处，带行号，前后各 3 行：

```json
{"path":"config/app.yaml","replaced":"2..2","total_lines":3,"around":"1: name: billing\n2: port: 9443\n3: region: eu-west\n"}
```

这样改完不用再读一次就能核对（写完读回的比例约 85%，每次读回多一步）。

### 2.4 write_file / append_file 的行号护栏

description 不变。content 的每一个非空行都匹配 `^\d+: `，而且数字从某个值开始连续递增时，**拒绝写入**并报错：

```
content 里每一行都带着 "N: " 行号前缀，这是 read_file 显示用的，不属于文件内容。去掉前缀后再写。
```

replace_lines 的 content 也做同样的检查。

- 只在"连续递增"时拒绝。YAML 里 `1: a` 这种单行，或者不连续的数字开头，都**不许**误拦。

### 2.5 search_text

description 不变。path 为空或 `.` 时跳过 `.web/`，path 以 `.web` 开头时只在其中搜。

这样做的原因：b22a 要教"本地查不到就上网"，网页存档不能混进"本地搜索"的结果，否则模型会分不清证据来自本地还是网页。

### 2.6 web_fetch

```json
{"name":"web_fetch","description":"Fetch up to four public web pages as readable Markdown. A short page comes back whole; a long page is saved under .web/ and only its opening lines and outline come back, so read the rest with read_file or search_text.","arguments":{"urls":["https://example.com/page"]}}
```

Parameters 不变（`urls`，1–4 个）。这样训练集里已有的 154 次 web_fetch 调用格式依然有效。

**取正文**：

1. 先用本地抽取：直接抓 HTML，用 `codeberg.org/readeck/go-readability/v2` 取正文，再用 `github.com/JohannesKaufmann/html-to-markdown/v2` 转成 Markdown。10-19 实测解析每页 1–28 毫秒，GitHub、arXiv 的导航栏都能去掉，4 个可读页面的事实全部保住。
2. 本地抽取失败（HTTP 错误、正文少于 200 字符、命中反爬页）时，按 App 设置里的顺序回退到 Tavily / DeepSeek（1fb46b5a 已有这个顺序设置）。反爬的判断：正文含"请完成下面的验证""verify you are human""Just a moment"之一。携程就会返回这种页面。
3. 评测和训练渲染不联网：正文直接取 `web_fixture[].content`，后面的步骤完全相同。

**分页面处理**。按 RWKV World 词表计 token（已有的 `TokenCount`）：

- **短页面**（≤ 3000 token）：整页放进 `content`，和 agent-tool-v2.0 一样。
- **长页面**（> 3000 token）：
  - 整页 Markdown 存为 `.web/{n}-{host}.md`。`n` 是本会话第几个存下来的页面，从 1 开始；`host` 去掉 `www.`，只保留 `[a-z0-9.-]`。例：`.web/1-github.com.md`。
  - `content` 只放开头若干行，按整行截取，不超过 1200 token。
  - `outline` 列出 Markdown 标题行（`#` 到 `###`），带行号，最多 40 条。标题少于 3 个时不给 outline。
- 一次调用里所有页面的 `content` 加起来不超过 6000 token，按 URL 顺序分配。超出预算的短页面也按长页面处理（存文件、只给开头）。

**长页面返回样例**：

```json
{"pages":[{"source_id":"page-1","url":"https://github.com/BlinkDL/RWKV-LM","title":"RWKV-LM","content":"# RWKV: Parallelizable RNN with Transformer-level LLM Performance\n\nRWKV is an RNN with transformer-level LLM performance…\n","saved_as":".web/1-github.com.md","total_lines":812,"outline":["1: # RWKV: Parallelizable RNN…","45: ## Installation","120: ## Usage","388: ## RWKV-7"]}],"note":"有的页面较长，只显示了开头。全文已存到 saved_as 里的文件：用 read_file 的 start_line 跳到 outline 里的章节，或用 search_text 在 .web/ 里搜关键词。"}
```

- 短页面不带 `saved_as`、`total_lines`、`outline`，返回形状和 agent-tool-v2.0 完全一样。
- 空页面、部分为空的提示语（`emptyWebFetchNote`、`partialWebFetchNote`）**原样保留**，它们是 10-16 探针挑出来的措辞。
- 长页面 note 与空页面 note 同时出现时，用 `；` 连成一条，长页面 note 在前。
- `truncated` 字段不再出现。agent-tool-v3 里不会再有"内容被丢掉"的情况，只有"内容存进了文件"。

### 2.7 .web/ 存档区

`.web/` 是会话级的只读存档区，规则必须全部满足：

| 规则 | 理由 |
|---|---|
| read_file、search_text、list_files、bash 都能读（bash 里路径是 `/workspace/.web/…`） | 模型用已经训练过的工具接着读，不新增工具 |
| write_file、replace_lines、append_file 写入 `.web/` 时报错 `.web/ 是网页存档，只读。`；bash 写入也不生效 | 存档内容必须和网页一致，否则可恢复压缩就不可信了 |
| **不出现在 App 的文件改动面板**（`StagedWorkspace.Changes()` 过滤掉 `.web/` 前缀），确认改动时也**不写入**用户磁盘（`Resolve` 跳过） | 用户没要求保存网页，面板里多出文件会让人困惑 |
| 没有打开工作区时也能用：此时文件工具对其他路径照旧报"先打开工作区"，对 `.web/` 路径照常工作 | App 默认可以不开工作区直接聊天、上网 |
| 评测和渲染时 `.web/` 放在临时目录，不进 `expect.files` 的比较；`unchanged` 检查忽略它 | 否则所有网页题的"无关文件不变"判据都会失败 |
| 文件名只由调用顺序和 host 决定，不含时间、随机数 | 训练数据靠 harness 重放生成，重放两次必须逐字节一致 |

**实现方式（M2 照此做，不许换）**：在 `StagedWorkspace` 里加一个 `scratch` 前缀（固定为 `.web/`），由 web_fetch 通过 sidecar 写入 overlay（这样 bash 能看到），`Changes()` 和 `Resolve()` 过滤掉这个前缀。不许另做一个只有 read_file 认识的内存存储——那样 bash 看不到，模型用 `grep` 查存档时会得到"文件不存在"。

### 2.8 web_search

description 改为 `Search the public web and return titles, URLs, snippets, and source IDs.`，其余不变。

原文里的 "with Brave" 已经不对：10-17 起中文查询走 DeepSeek。

### 2.9 calculator

description 改为：

```
Evaluate arithmetic with +, -, *, /, %, ^, parentheses, and abs/min/max/round/sqrt/pow/ln/log10/exp. Use precision to format decimal or money results.
```

- 新增 `^`（乘方，右结合）和 `sqrt pow ln log10 exp`。考卷里有 6 次"function is not allowed"、6 次"unsupported construct"，都出在开方、乘方这类写法上。
- 报错文字统一加上一条可以照做的建议，例如：

```
不支持 integrate。calculator 只做算术和上面列出的函数；更复杂的计算用 bash：awk 'BEGIN{printf "%.4f\n", 表达式}'。
```

### 2.10 data_query

description、参数都不变，只放宽校验（考卷两遍里这三类报错合计 26 次）：

| 情况 | agent-tool-v2.0 | agent-tool-v3 |
|---|---|---|
| `sum/avg/min/max` 同时给了 `field` 和 `expression` | 报错 | 用 `expression`，结果里加 `"ignored":"field"` |
| `sum/avg/min/max` 两个都没给 | 报错 | 仍报错，但改成：`sum 需要 field（列名）或 expression（按行计算的式子），例如 {"operation":"sum","field":"qty"}。` |
| `count` 带了 `field` 或 `expression` | 报错 | 忽略多余的参数，照常计数，结果里加 `"ignored":"field"` |

### 2.11 目录顺序与系统提示词

- 目录顺序只在 `internal/agent/product/tools.go` 的 `Tools()` 一处定义；评测的 `buildWorkToolCatalog` 对 agent-tool-v3 **必须**调用它，不许再自己拼。现在两份代码里 bash 和 get_weather 的先后顺序不一样（产品是 weather 在前，评测是 bash 在前），这是 10-15 记下的漂移。
- 系统提示词里 bash 那一句改为：`bash runs in a sandbox whose /workspace is the user's workspace; use it for listing, counting, filtering or changing many files at once. Read single files with read_file, which shows numbered lines one screen at a time.`

### 2.12 旧数据迁移规则

训练行只能由 harness 重放老师的动作脚本生成（`docs/design/corpus-g1k-wire-format.md`、`bench/distill/common/harness-corpus-render.md`）。换成 agent-tool-v3 后，老师的**动作**照旧重放，工具**返回值**按新规则重新生成。动作按下表改写：

| 老师原动作（agent-tool-v2.0） | 重放时改成（agent-tool-v3） | 轨迹怎么处理 |
|---|---|---|
| `read_file {"path":P}`，文件 ≤ 200 行且 ≤ 12KB | `read_file {"path":P,"start_line":null,"end_line":null}` | 直接保留：返回内容一样，只是多了行号 |
| `read_file {"path":P}`，文件超过一屏 | 同上 | **整条轨迹（这一用户轮）作废，重新跑老师**。老师当时看到了整个文件，后面的思考和答案可能用到第 200 行以后的内容，新返回值撑不住 |
| `read_lines {"path":P,"start_line":a,"end_line":b}` | `read_file {"path":P,"start_line":a,"end_line":b}` | 保留 |
| `replace_lines`，end_line 超出末行，原来报错 | 动作不变，现在会成功 | **作废重跑**：后面的步骤是在处理报错，和新返回值对不上 |
| `web_fetch`，页面 ≤ 3000 token | 不变 | 保留（v2.1 训练集最长的网页只有 830 字符，全部属于这一类） |
| `calculator` / `data_query`，原来报错、新版本会成功 | 动作不变 | **作废重跑**，理由同 replace_lines |
| 其他 | 不变 | 保留 |

**v2.1 包的影响面**（10-19 在 `final-20261018-ctx16k` 上统计）：1889 条用户轮轨迹里，有 143 条（7.6%）读到了超过一屏的文件，涉及 97 道题（tab 72、log 15、hyb 7，其余各 1）。replace_lines、calculator、data_query 那几类的数量 **待 M0 统计**，要求按动作类型分别列出条数和题号。

- 作废的轨迹**不许**为了凑数而保留"截掉后半段"的版本。截掉以后，老师的答案就没有依据了，正好训练出"没读到也照样答"的坏习惯。
- 重跑老师用 v2.1 同一套设置（千问 3.7 Flash、`--harness app`、24 路并发），见 `bench/distill/tools/v21/README.md`。

### 2.13 题库迁移

- 题库（`bench/exam`、`bench/workbank`、`bench/distill/*/cases`）里出现 `read_lines` 的地方——`tool_policy.must_offer` / `never_offer`、`required_tools`、`forbidden_tools`、`max_calls` 的键——一律改成 `read_file`。考卷里提到 read_lines 或 replace_lines 的题有 22 道，workbank 有 2 道。
- 用一次性脚本改写，放在 `scripts/migrate_work_v3_cases.py`，改完的题 `tags.version` 加 1。
- 目录由跑分参数选，不由题目选：`rwkv-cli` 的 `--tool-catalog`，以及 `--harness app/raw` 时强制使用的目录（现在写死为 agent-tool-v2.0，见 `cmd/rwkv-cli/main.go` 约 1868 行）。agent-tool-v3 落地后：
  - `--harness app` 默认改为 agent-tool-v3；
  - `--harness app --tool-catalog agent-tool-v2.0` **必须仍然可用**，用来按老口径复现历史跑分。所以 `product.Tools()` 要加一个目录版本参数，agent-tool-v2.0 分支原样保留。
- `bank lint` 的目录契约（`workCatalogNames`）加上 agent-tool-v3 的 13 个工具名。

## 3. 接口契约

- `eval.WorkV3ToolCatalogName = "agent-tool-v3"`；`IsWorkToolCatalog` 认识它。
- `product.Tools(set ToolSet, b Backends)` 增加 `set.Catalog`（`"agent-tool-v2.0"` 或 `"agent-tool-v3"`，零值为 agent-tool-v3）。agent-tool-v2.0 分支在内部调用原来的构造函数。
- `buildWorkToolCatalog("agent-tool-v3", …)` 只调用 `product.Tools`，然后用 `requireWorkCatalogShape` 校验工具名。
- `WebFetchProvider` 接口不变。本地抽取作为一个新的 provider，排在 App 设置里"先用哪个后端读网页"的列表最前面。
- `StagedWorkspace` 新增 `ScratchPrefix = ".web/"`：`Changes()` 和 `Resolve()` 过滤这个前缀；对这个前缀的写入，只有 web_fetch 用的内部方法能执行。

不许做的事：

- 不许在 `agent` 包外再拼一份工具顺序。
- 不许让 web_fetch 返回值里出现绝对路径或临时目录名（例如 `/var/folders/…`）。路径只能是 `.web/…`，否则重放出来的训练行每次都不一样。

## 4. 实现注意事项（这个项目特有的坑）

### 4.1 不能动坏 agent-tool-v2.0

1. agent-tool-v2.0 的目录哈希、提示词字节、返回值必须完全不变。M1 第一件事是加一条金样测试：用固定工作区跑一遍 agent-tool-v2.0 的每个工具，把 `workToolCatalogHash` 和返回 JSON 存成 golden，之后每个里程碑都要过这条测试。
2. 共用的辅助函数（如 `readFileLinesWithFS`）要改行为时，复制一份新的给 v3 用，不要在原函数上加分支。v2 的 64KB 截断"bug"在 v2 里也要原样保留——历史跑分就是在这个行为下得出的。

### 4.2 行号

3. 行号格式固定为 `N: `（数字、冒号、一个空格），和 read_lines、replace_lines 现有的格式一致。不许改成 `cat -n` 那种制表符格式——模型在 read_lines 上见过的就是冒号格式。
4. 文件最后没有换行时，最后一行照常编号，不许多出一个空行。

### 4.3 网页

5. 抽取前后都不许对正文做 `strings.TrimSpace` 以外的规整（比如合并空行、改标题级别）。outline 里的行号必须和存下来的文件逐行对得上，规整一步就错位。验收里有专门的检查。
6. 本地抽取遇到非 UTF-8 页面时要按 HTTP 头或 meta 标签里的字符集转码，转不了就当失败、走回退。不许把乱码存进 `.web/`。
7. 评测里 `web_fixture` 的 `content` 本身就是 Markdown，**不再**经过 readability（readability 只处理 HTML）。直接按 §2.6 的长短规则处理。

### 4.4 训练数据

8. 训练行里思考、动作的文本不变，只有 `<tool_response>` 的内容变了。M5 的渲染结果要能和 v2.1 的行逐行对上：同一条轨迹、同一步，`loss_spans` 覆盖的文本必须完全相同。不同就说明重放顺序或拦截逻辑变了，要先查清楚，不许直接接受。
9. 作废轨迹（§2.12）重跑老师仍没通过的，要按题写进 `bench/distill/common/exclude.jsonl`（字段 `case_id`、`reason`、`batch`），`reason` 写 `work-v3-window`、`work-v3-replace-clamp` 之类。不许直接从包里悄悄删掉。

## 5. 里程碑

每个里程碑结束时都要跑：

```bash
go test ./internal/agent/... ./internal/lab/... ./cmd/...
```

### M0 —— 影响面统计（0.5 天，不用 GPU，**阻塞项**）

不先做这一步，M5 不知道要重跑多少老师，也不知道 200 行 / 12KB 是否合适。

- 输出 `docs/evaluations/work-v3-m0/REPORT.md`，必须包含：
  1. v2.1 包（`local/runs/distill/v21/final-20261018-ctx16k/train-rows.jsonl`）里，按 §2.12 每一类动作的轨迹条数和题号清单（JSON 附件）。
  2. 考卷两遍（`local/runs/exam-20261017/v21-lr2e-5-e2-think-full-k{0,1}`）里 read_file 返回值的行数、字节数分布，以及"200 行 / 12KB"会截到多少次。
  3. 如果建议改 200 / 12KB，要写清理由和改后的影响数字。**用户同意前不许改。**

### M1 —— 文件工具（2 天）

- 按 §2.1–§2.5 实现，加 §4.1 的 agent-tool-v2.0 金样测试。
- 单测必须覆盖以下情况，每条都要有一个**故意改坏就失败**的版本：
  - 5000 行的文件：不给行号时只返回 200 行，note 逐字等于模板。把 note 里的 `200` 改成别的数，测试必须失败。
  - 每行 100 字节、共 300 行的文件：在 12KB 处截断，返回不到 200 行。
  - 100KB、3000 行的文件：读 `start_line=2900` 能读到第 2900 行（agent-tool-v2.0 的 read_lines 读不到）。
  - replace_lines 的 `end_line=999` 落在 3 行的文件上：成功，`end_line_clamped: true`。
  - write_file 的内容是 `1: a\n2: b\n3: c`：被拒；内容是 `1: a`：照常写入。
  - agent-tool-v2.0 金样：故意在 v2 的 read_file 描述里加一个空格，金样测试必须失败。

### M2 —— 网页（2–3 天）

- 按 §2.6–§2.8 实现，包括 `.web/` 存档区。
- 单测：
  - 6000 token 的 fixture 页：返回 `saved_as`、`outline`；用 read_file 读 outline 里任意一个行号，该行内容必须就是那个标题。在 Markdown 处理里加一步合并空行，这个检查必须失败。
  - 写入 `.web/x.md`：报只读错误。`StagedWorkspace.Changes()` 里没有 `.web/`。
  - 不开工作区：read_file 读 `.web/1-…md` 成功，读 `a.txt` 报"先打开工作区"。
  - 同一组 fixture 重放两次，返回 JSON 逐字节一致。
- 真实网页冒烟（联网，手动跑）：GitHub README、arXiv 摘要页、一个中文新闻页、携程（预期走回退）。结果贴进 PR 描述。

### M3 —— calculator / data_query（0.5 天）

- 按 §2.9–§2.10 实现。单测：`sqrt(2)`、`2^10`、`pow(1.05,12)` 结果正确；`integrate(x)` 报错文字里含 `awk`。

### M4 —— 目录、题库与提示词（1 天）

- 按 §2.11、§2.13、§3 实现，写好迁移脚本，更新 golden prompt（`internal/agent/testdata/golden_prompt/`）。
- 验收：

```bash
go build -o local/bin/rwkv-lab ./cmd/rwkv-lab && go build -o local/bin/rwkv-cli ./cmd/rwkv-cli
local/bin/rwkv-lab bank lint                                   # workbank，10-19 基线：148 题 0 违规
local/bin/rwkv-lab corpus loadcheck --cases bench/exam/cases   # 10-19 基线：190 题能加载
local/bin/rwkv-lab corpus loadcheck --cases bench/distill/v2.1/cases
python3 scripts/migrate_work_v3_cases.py --check               # 迁移后再跑一遍，必须没有任何改动
```

### M5 —— 训练数据重渲染与补老师（1–2 天，按 M0 的数字定）

- 用 agent-tool-v3 重渲染 v2.1 全部路径（命令同 `bench/distill/tools/v21/README.md`，把 `--tool-catalog agent-tool-v2.0` 换成 `agent-tool-v3`）。
- 按 §2.12 作废并重跑老师，按 §4.4 第 8 条逐行对齐检查。
- 产出 v2.1-v3 包，并和 v2.1 原包比较行数、条数、各场景的条数。

### M6 —— 重跑基准（GPU，约 1 天）

- 新目录下，下面每一组都用新考卷跑两遍（口径同 `docs/evaluations/exam-v21-20261017/REPORT.md` §1，只把目录换成 agent-tool-v3）：基模、v2.0 MiSS、v2.1 lr2e-5（老权重，没见过 agent-tool-v3）。
- 另建一套**长网页探针**（20–30 题，网页按真实长度，任务是写报告、摘要、多页对比）和**大文件探针**（从考卷里读过大文件的 59 题中挑），两套目录都跑。
- 验收：报告写清新旧目录下的分数差，以及哪些题因为目录变化翻转。老权重在新目录下掉分是预期结果，**不是 bug**——它们从没见过行号和 `.web/`。

## 6. 版本与可比性

- 跑分记录里的目录哈希（ledger 的 `tool_catalog` 及哈希）不同的两次跑分不能直接比较。agent-tool-v3 落地后，所有新数字都和 M6 的新基准比。
- **版本号规则（2026-10-21 修订，取代原来的“开新目录名”）**：目录名写作 `agent-tool-v主.次`，定义在 `internal/agent/product/catalog_version.go`，`run.json` 和 ledger 记录完整版本号。
  - **主版本号**：模型看到的东西变了，也就是任何一个工具的名字、描述、参数说明或 schema 变了。目录哈希会变，训练数据要重新渲染，基准要重跑。例：v2 → v3。
  - **次版本号**：只改工具行为（参数容错、提示语、报错文字、返回里多加字段），目录哈希不变。跑分记录只能靠版本号区分，基准同样要重跑。例：v3.0 → v3.1（§10–§11）。
  - 现有版本：`agent-tool-v1.0`（原 work-v1）、`agent-tool-v2.0`（原 work-v2，冻结）、`agent-tool-v3.0`（原 work-v3，10-21 修复前，代码里已不可复现，指定它会报错）、`agent-tool-v3.1`（当前 App 目录）。
  - 旧名只在读取端保留为别名：命令行参数、考卷清单、题目文件里的 `work-vN` 照常可用（题目文件按内容算考卷哈希，不改）。写出来的地方（CLI 帮助、`run.json`、ledger、文档、脚本）一律用新名。历史 `run.json` 里的 `work-v3` 在 ledger 中记作 `agent-tool-v3.0`。
  - 每次改动都要更新 `catalog_version.go` 里的版本号，以及 `internal/agent/eval/workcatalog_v2_golden_test.go` 里固定的哈希（主版本号变化时）。

## 7. 参考：成熟框架的做法（2026-10-19 查）

| 框架 | 读文件 | 改文件 | 读网页 |
|---|---|---|---|
| Claude Code | Read：`file_path` + `offset`/`limit`，默认最多 2000 行，带行号 | Edit：`old_string`/`new_string`，必须唯一匹配；Write 整个覆盖 | WebFetch：`url` + `prompt`，由小模型按问题处理页面，可用 `offset` 接着读；工具返回默认上限 25,000 token |
| Anthropic text editor 工具 | `view` + `view_range`，带行号；可配 `max_characters` 截断 | `str_replace`（必须唯一）、`insert`（按行号）、`create` | — |
| Gemini CLI | `read_file`：`file_path`、`start_line`、`end_line` | `replace`：`old_string`/`new_string`/`allow_multiple`；`write_file` | `web_fetch`：只有 `prompt` 参数，网址写在 prompt 里 |
| MCP fetch 服务 | — | — | `max_length`（默认 5000 字符）+ `start_index` 翻页 |
| SWE-agent | 一次显示 100 行的窗口，带行号、总行数、上下翻页 | 按行区间替换，改完自动 lint 并显示结果 | — |
| Codex CLI | 用 shell 读 | `apply_patch` 补丁格式 | 有 web_search |
| Manus | 把文件系统当外部记忆 | — | 压缩必须"可恢复"：去掉网页正文时保留网址，去掉文档内容时保留路径 |

对我们有用的三条：

- **读文件都带行号、都按窗口读**，没有一家一次把整个大文件塞进上下文。
- **截断时要告诉模型下一步怎么做**。Anthropic 的工具写作指南原话是 "steer agents with helpful instructions"。我们 bash 的截断提示已经这样做了，read_file 还没有。
- **网页内容存到外面、需要时再读**（Manus），比翻页参数或让模型先摘要更适合我们：不加新参数，不需要外部模型。

来源：

- [Anthropic: Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Anthropic text editor tool](https://platform.claude.com/docs/en/docs/agents-and-tools/tool-use/text-editor-tool)
- [Gemini CLI tools reference](https://geminicli.com/docs/reference/tools.md)
- [MCP Fetch server README（Glama 镜像）](https://glama.ai/mcp/servers/@modelcontextprotocol/git/blob/04cce79b4c2bbaa313095e9c2a466381f5fd1e64/src/fetch/README.md)
- [Manus: Context Engineering for AI Agents](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)
- [SWE-agent 论文 arXiv 2405.15793](https://hyper.ai/papers/2405.15793)
- [OpenAI apply_patch 指南](https://developers.openai.com/api/docs/guides/tools-apply-patch)
- Claude Code 的 Read / Edit / WebFetch 参数取自本会话里工具的实际定义。

## 8. 实现记录：与上文规格的出入（2026-10-19，M1–M4 已实现）

实现时改了下面几处，**以这里为准**：

| 位置 | 原规格 | 实际实现 | 原因 |
|---|---|---|---|
| §2.1 读到末尾之后 | `第 {a} 行之后没有内容` | `文件只有 {total} 行，没有第 {a} 行。` | 原句在 start_line 大于总行数时读不通 |
| §2.1 区间超过 200 行 | 不得超过 | 按一屏截断并给出 note，不报错 | 报错只会让模型重试一次；截断后它照样能接着读 |
| §2.3 返回字段 | `replaced: "2..2"` | 沿用 agent-tool-v2.0 的 `replaced_from` / `replaced_to` / `total_lines`，加 `around` 和 `end_line_clamped` | 和老返回值保持一致，训练过的字段名不变 |
| §2.7 bash 写 `.web/` | 不生效 | 能写进暂存区，但不出现在改动面板，也不落盘 | 拦 bash 写入要改 sidecar；不落盘已经够用 |
| §2.7 无暂存区时 | — | 存档放在主机临时目录，read_file / search_text / list_files 能读，bash 读不到 | 没有暂存区就没有 bash 能看到的共享文件系统 |
| §2.9 `^` 乘方 | 新增 `^` | **不加**，乘方写 `pow(a, b)`；遇到 `^` 或 `**` 时报错，并提示写法 | Go 的表达式解析里 `^` 和 `+` 同级，`2*3^2` 会被算成 36，而且不报错 |
| §2.12 read_file 动作 | 补上 `start_line:null,end_line:null` | 原样保留 | 参数解码不强制 required，`{"path":P}` 在 agent-tool-v3 里照常可用；只有 read_lines 改名为 read_file |
| §2.13 题库迁移 | 写迁移脚本改题目文件 | **不改题目文件**。用 agent-tool-v3 跑分或渲染时，在运行时把题目里的 `read_lines` 当成 `read_file`（`eval.adaptCasesToCatalog`） | 题目文件一改，agent-tool-v2.0 就复现不了历史分数 |
| §3 非 App 路径 | — | `--tool-catalog agent-tool-v3.1` 不加 `--harness app` 时也走 `product.Tools`，但 bash 用的是真实时钟 | 现行的跑分和渲染都用 `--harness app`，这条路径基本不用 |

**已验证的内容：**

- `go test ./internal/... ./api/ ./cmd/rwkv-cli/` 全部通过。
- agent-tool-v2.0 的两条金样测试都会在改坏时失败：故意往 v2 的 read_file 描述里加一个空格，目录哈希测试失败；故意改动 note 文字，v3 测试失败。
- 用 agent-tool-v3 重渲染 b21p（75 题）：201 行全部生成，每行训练片段的文本和 v2.1 原包逐字相同，作废的 6 题也和原来一样。工具返回值已经是带行号的新格式，系统提示词里的 bash 那句也换成了新句子。
- 真实网页冒烟（`RWKV_LIVE_WEB=1`）：GitHub README 约 8 万字，会存档；arXiv 摘要页正常；gov.cn 读不到，交给 Tavily / DeepSeek 回退；携程只读到页脚（约 1400 字），**没有**被识别成反爬页。这是已知缺口。

## 9. 修订：长网页改为截断，不再存档（2026-10-20）

用户拍板：`.web/` 存档再读对 7B 模型要求太高（多一步，还要照抄路径、按目录跳读），先不做。§2.6–§2.7 的存档行为作废，`web_fetch` 改成下面这样，**以本节为准**：

| 项 | 现在的行为 |
|---|---|
| 去链接 | 计数之前先删掉 Markdown 图片，内联链接只保留文字（`[文字](网址)` → `文字`）。页面本身的网址仍在结果的 `url` 里 |
| 预算 | 一次调用里所有页面**共用 6000 token**。页面从短到长分配，每页最多拿剩余预算的平均份额：短页不会为长页让位，两个长页对半分 |
| 超出 | 保留开头的整行，标 `truncated: true`，note 为「有的页面较长，只给出了前面一部分（truncated 为 true），后面已省略；重复抓取同一网址也拿不到更多内容。」 |
| 描述 | `Fetch up to four public web pages as readable Markdown. A long page comes back cut to its opening part.` |
| 计数 | App 远端模式也用随包的 RWKV 词表计数（`api/session.go` `webTokenizerPath`）。之前远端只能粗估，代码多的页面会少算约 35% |
| 不变 | 本地 go-readability 排第一、读不到再回退 Tavily / DeepSeek（§2.6 抓取链）照旧 |

`.web/` 相关的东西已全部删除：`saved_as` / `total_lines` / `outline` 字段，`WebArchive` / `PageStore`，无工作区时的主机临时目录（`WorkspaceV3Options.ScratchDir`），`list_files` / `search_text` 跳过 `.web/`，写入 `.web/` 报只读，以及改动面板隐藏 `.web/`（`StagedWorkspace.HideFromReview`）。用户工作区里如果真有 `.web` 目录，现在和普通目录一样对待。

**依据**是 10-20 的长网页容量探针（`local/runs/probe-longpage-20261020/`，不入库）：
- 方法：4 个真实网页截到 2K–20K token，按 App 第二步的提示词发给 MiSS r16-lr2e-5-e2。
- 总结：到约 12K 都不崩，16K 以上英文代码页开始没有终答。
- 事实题：3K 以内全对，3–6K 约 50%，6K 以上掉到 2–4 成。
- 真实网页去掉链接网址后，中文维基 37K → 18.7K token。

**影响：**
- b22f（8–16K 长任务，80 题）是按存档设计的，已移到 `bench/distill/v2.2/cases-shelved/`，以后再说。
- b22c 有 8 题的页面约 4–5K token，现在会整页返回，判据不变。
- 工具描述变了，所以 agent-tool-v3 下渲染的训练行（v2.1 重放的 `kept/`）要重新渲染一次才和 App 一致。不需要重跑老师。

## 10. 修订：四处“结果悄悄出错”（2026-10-21）

10-21 工具审阅时，用临时探针实测出四处“不报错、但结果是错的”。只改了 agent-tool-v3 的行为，描述、参数和目录哈希都没变；agent-tool-v2.0 保持原样（每条都有测试锁住）。

| # | 工具 | 以前 | 现在 |
|---|---|---|---|
| A1 | `data_query` | filter 只判断“完全相等”，`{"qty":">3"}` 返回 `matched_rows: 0`，不报错 | 值以 `>` `>=` `<` `<=` `!=` `<>` `=` `==` 开头时按比较处理：两边都是数字按数值比，都是日期按时间比，否则按文字比；值是数组时表示“等于其中任意一个” |
| A2 | `append_file` | 原样追加字节：原文件末尾没换行时 `beta` + `gamma` 变成 `betagamma` | 原文件末尾没换行就先补一个；content 末尾也补一个；用原文件的换行风格（CRLF 文件追加 CRLF） |
| A3 | `list_files` `search_text` | 名叫 `build`、`dist` 的目录整个跳过，结果里没有任何提示 | 只跳过 `.git` 和 `node_modules` |
| A4 | `read_file` `replace_lines` | CRLF 文件的 `\r` 漏进内容（`"1: one\r\n"`）；replace_lines 写回时全部改成 LF | 读取时去掉行尾 `\r`；写回时沿用原文件的换行风格（CRLF 占多数就按 CRLF 写） |

影响面（10-21 扫描 `bench/**/case.json`）：exam、workbank、holdout 一题都不涉及。build/dist 下有文件的题：v2.0 2 题、v2.1 7 题、v2.2 5 题、bashprobe 4 题，都是以 build 目录本身为对象的题（删构建产物、提示注入要求删 build）。工作区里有 CRLF 文件的题：v1.4 2 题、v1.41 1 题、v2.0 2 题、v2.1 1 题。已经出好的训练包不变；以后用 agent-tool-v3 重新渲染时，这些题里 list_files、search_text、read_file 的返回会和旧包不同。

## 11. 修订：参数容错与返回提示（2026-10-21）

接着 §10，把 10-21 审阅里“不用改描述就能修”的问题也修了。同样只改 agent-tool-v3 的行为，描述、参数和目录哈希都没变：哈希仍是 `70cca57d…`，由 `TestWorkV3AppCatalogHashPinned` 固定。agent-tool-v2.0 原样不动，每一条都有测试检查 v2 的旧行为。

| # | 工具 | 现在的行为 |
|---|---|---|
| B1 | `web_fetch` | 接受单数 `url`（字符串或数组）、把 `urls` 写成字符串、不带协议的 `example.org/a`（补 `https://`）；超过 4 个网址时只抓前 4 个，note 里列出没抓的那些 |
| B2 | `list_files` `search_text` `web_search` | `max_results` `max_depth` 超过上限时按上限处理，小于 1 时按默认值处理，不再报错 |
| B3 | `read_file` | 接受 `file_path`（等同 path）、`offset`（起始行）和 `limit`（行数）；同时给了 start_line/end_line 时以它们为准 |
| B3 | `data_query` | 接受 `limit`（最多列几行，上限 100） |
| B4 | `calculator` | 解析前先规整：× ÷ 和全角括号、逗号、加减号；`math.` 前缀；末尾的 `=`；千分位（只在没有函数调用时去掉，`pow(2,100)` 保持原样）；数字后面的 `%` 当百分号（`200*15%` 就是 30，`10%3` 仍然是取余）。返回的 `expression` 是规整后的式子。`math.sqrt` 这类写法不再报旧文案 “only abs, min, max, and round” |
| B5 | `data_query` | 带千分位或货币符号的单元格（`"1,200"`、`"$12.50"`）读作数字，sum、比较和 filter 都按数字处理；匹配的行没有全部列出时附 note：`共匹配 N 行，只列出了前 M 行…` |
| C1 | `datetime` | now 加 `weekday`；compare 加 `days_between`（日期之间按日历天数算）、`left_weekday`、`right_weekday`；add 支持 `3d` `2w` `1d12h` `3天` `1 month` `-1y`，结果加 `weekday`；op 也接受 today、diff、between 等写法；now 不再因为带了 args 报错 |
| C2 | `search_text` | 没有匹配时附中文 note；query 看起来像正则（含 `|` `*` 等）时，note 说明只做字面匹配 |
| C3 | 文件工具、`data_query` | 路径不存在时报 `找不到 X：工作区里没有这个文件或目录。先用 list_files 或 search_text 确认路径。`；read_file 读到目录、list_files 列的是文件，也都改成中文并说明该用哪个工具。非 UTF-8 和二进制文件的报错按 §2.1 保持不变 |

**对跑分的影响**（10-21 用 `exam-20261017`、`exam-20261020`、`exam-20261021` 的轨迹估算）：

- 这几轮考卷记录的目录都是 **agent-tool-v2.0**（哈希 `be0c3178…`），这次没有改动 v2，历史分数不受影响。agent-tool-v3 还没有考卷基准（§5 的 M6）。
- 原本报错、现在会成功的调用很少。v2.1 lr2e-5 每遍涉及 2–4 题（其中 1–3 题当时失分），比两遍之间的波动（299 对 294）还小。G1L 基模涉及 18 题（其中 13 题失分），主要是 web_fetch 网址写法 12 次、datetime 写法 7 次。
- 结果照样成功或失败、只是文字变了的调用多一些：找不到路径的中文报错 33–133 题、搜索空结果的 note 14–67 题、datetime 多出的字段 12–20 题。这些会改变模型看到的内容，影响方向要实际跑过才知道。
- 注意：修复前后 agent-tool-v3 的目录哈希相同，ledger 区分不出这两种行为。目前 agent-tool-v3 只有蒸馏老师的轨迹，没有考卷跑分，所以暂时不构成问题；以后的 agent-tool-v3 基准都应该在这次提交之后跑。
- 训练数据：已出的包里，agent-tool-v3 的工具返回是修复前的行为。重新渲染后，这些路径的 `<tool_response>` 会变（每一次 datetime 调用都会多出字段），`loss_spans` 覆盖的文本不变。
