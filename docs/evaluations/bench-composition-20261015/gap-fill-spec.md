# 考卷补题 —— 实施规格书

> 给执行出题的 Agent 看。文中「必须 / 不许」是硬约束，每条都附了理由；不确定时照做，别「优化」。
> 核心章节是 **§2 补题清单**：每一批要出什么、出多少、长什么样、怎么判分。其余章节是外壳。
> 背景：`REPORT.md`（同目录）第 8～9 节；题库总表：`bench/exam/SUITES.md`。

## 0. 目标

新考卷（`bench/exam/full.json`，380 题）的原则是：**每道题都是用户在 App 里真实会做的一件事，并且按 App 的默认配置来考**（g1k、文件 / web / 天气 / bash 全开、文件改动先暂存）。题目总量够了，但有几块明显偏少：中文的改文件、中文的直接回答、用户追问、长输入、查不到时要说明。这份规格书列出要补的 6 批共 **108 题**。新题放在 `bench/exam/cases/`，`rwkv-lab exam build` 会自动并入完整考卷。

最关键的取舍：**宁可少出，不出判不准的题**。验收时用 DeepSeek 盲解；DeepSeek 做不对的题，要么修题，要么在 NOTES 里写明为什么它就是难，不能为了凑数量放进来。

## 1. 总览

| 批次 | 补什么 | 题数 | 语言 | 任务类型（`Task`） | 现状 → 目标 |
|---|---|---|---|---|---|
| G1 | 中文改文件、写产物 | 24 | 中 | write | 中文 19 → 43 |
| G2 | 中文直接回答（闲聊、概念、该反问、做不到） | 16 | 中 | answer-direct | 中文 21 → 37 |
| G3 | 用户追问、改需求（2～3 条用户消息） | 24 | 中 12 / 英 12 | 各类均匀 | 英文追问 14 → 26，中文写文件追问 2 → 8 |
| G4 | 长输入（大文件、截断、只需一小块） | 18 | 中 9 / 英 9 | compute / find-read | 33 → 51 |
| G5 | 查不到时说明查了哪、缺什么 | 16 | 中 10 / 英 6 | find-read / external | 5 → 21 |
| G6 | 出错恢复（路径不对、链接失效、工具报错） | 10 | 英 6 / 中 4 | 各类 | 英文 14 → 20 |
| **合计** | | **108** | 中 75 / 英 33 | | 完整考卷 380 → 488 |

**不做的事：**
- 不改已有的题。旧题有问题记到交付说明里，由维护者处理。原因：旧题的内容哈希进了考卷清单，改一题会让所有历史成绩不可比。
- 不出订机票、发邮件**成功**这类题。工作区工具做不到；G2 里「做不到」的题考的是模型如实说明做不到。
- 不出子 Agent（spawn_agents）相关的题，它不在 App 默认工具集里。
- 不需要「工具未配置」这一类题（例如没填搜索 key 时如实告诉用户）。它需要评测给单题注入不可用的工具，目前还不支持，见 §7 的 TODO。

## 2. 补题清单（核心章节）

### 2.1 一道题由什么组成

每道题一个目录 `bench/exam/cases/<scenario>/<id>/`，里面恰好三个文件：

| 文件 | 内容 | 硬约束 |
|---|---|---|
| `case.json` | 题面、工作区文件、判分规则 | 格式见下方完整样例 |
| `verify.py` | 只读 `case.json`，独立重算正确答案并打印 JSON | `rwkv-lab bank verify` 会运行它，还会故意改坏 fixture 再跑一遍，确认答案会跟着变。所以答案必须从 fixture **算出来**，不许把答案常量写死 |
| `NOTES.md` | `## Traps` / `## Reference solution` / `## Why the answer is unique` 三节 | lint 会检查 NOTES 里写了答案值 |

**编号**：`<缩写>-9xxx` 已被 `bench/distill/v1.41` 占用。新题统一用 `<缩写>-6001` 起，缩写取自 `bench/workbank/tag-vocab.json` 的 `scenarios[].abbrev`（tab / log / cfg / doc / fs / scr / code / web / hyb / nt）。先用 `find bench -name case.json -path '*-6[0-9][0-9][0-9]/*'` 确认为空。原因：`exam build` 遇到重复 ID 直接报错，而且历史成绩按 ID 对齐。

**canary**：`description` 必须以 `EXAM-CANARY-<8 位小写十六进制>` 结尾，`verify.py` 首行注释和 `NOTES.md` 末行也写同一串。原因：训练语料管线按 canary 剔除测试题；不带 canary 的题迟早会漏进训练集（workbank 已经因此泄漏了 36 题）。

**完整样例（中文写文件题，来自 p13，可直接照抄结构）：**

```json
{
  "id": "cfg-8005",
  "description": "Change the production sync interval to 15 minutes in a two-section config while the staging section stays untouched; judged by pinned substrings. DISTILL-CANARY-9b2e6d41",
  "category": "config",
  "tags": {
    "scenario": "config",
    "task_type": "edit_value",
    "traps": ["TR-DECOY"],
    "trap_decoys": {"TR-DECOY": null},
    "axes": ["OBS"],
    "level": "L1",
    "family": "fam-holdout-cfg-edit-01",
    "answer_style": "natural",
    "ref_calls": 2,
    "fixture_bytes": 205,
    "status": "draft",
    "version": 1,
    "author": "llm:glm-5.3-flash-p13",
    "reviewer": null
  },
  "files": {
    "config/sync.conf": "[sync]\nendpoint = https://tracks.lanren-logistics.example/pull\ninterval_minutes = 30\nbatch = 200\n\n[staging]\nendpoint = https://tracks.staging.lanren-logistics.example/pull\ninterval_minutes = 10\nbatch = 50\n"
  },
  "turns": [
    {
      "prompt": "把正式环境的轨迹同步间隔从 30 分钟改成 15 分钟，其余内容原样保留。完成后，用一到三句话告诉我你改动了什么。",
      "expect": {}
    }
  ],
  "expect": {
    "files": {
      "config/sync.conf": {
        "contains": [
          "[sync]\nendpoint = https://tracks.lanren-logistics.example/pull\ninterval_minutes = 15",
          "interval_minutes = 15\nbatch = 200",
          "[staging]\nendpoint = https://tracks.staging.lanren-logistics.example/pull\ninterval_minutes = 10\nbatch = 50"
        ]
      }
    }
  }
}
```

对应的 `verify.py`（文件题打印 `{"files": {...}}`，问答题打印 `{"expected": ...}` 或 `{"expected_contains_any": [...]}`）：

```python
# EXAM-CANARY-xxxxxxxx : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
conf = case["files"]["config/sync.conf"]
assert "interval_minutes = 30" in conf
print(json.dumps({"files": {
    "config/sync.conf": conf.replace("interval_minutes = 30", "interval_minutes = 15"),
}}))
```

**tags 规则：**

| 字段 | 取值 | 理由 |
|---|---|---|
| `scenario` / `task_type` | 只能用 `tag-vocab.json` 里登记过的值 | lint 会拒绝未登记的值；确实需要新 task_type 时先停下来问维护者，不许自己往词表里加 |
| `traps` / `trap_decoys` | 陷阱 ID 来自 `docs/workbank/authoring-guide.md` §3；`trap_decoys` 写「掉进陷阱时会给出的那个错误答案」 | 复核时靠它判断模型错在哪 |
| `axes` / `level` | 见出题手册 §3、§4 | 考卷按难点出分，`axes` 标错会让分数归错类 |
| `answer_style` | 固定 `"natural"` | lint 据此禁止旧的「Reply with only the final answer / reply DONE」结尾 |
| `author` | `llm:<模型名>` | 出题模型**不许是 DeepSeek 或 Qwen**，它们是现役蒸馏老师。原因：老师出的题顺着老师自己的习惯，会让老师和学这个老师的模型虚高 |
| `status` | `"draft"` | LLM 出的题没有人工复核前一律 draft |
| `ref_calls` / `fixture_bytes` | 参考解的工具调用次数；工作区文件总字节数（可用 `rwkv-lab bank lint --fix` 回填） | 考卷按它们统计 |
| `exam_task` / `exam_difficulties` | 可选。只有在自动分类明显错时才写 | 自动规则见 `internal/lab/exam/derive.go`；写了就以它为准 |

**题面规则（每一批都适用）：**

1. **像真人在 App 里打字。** 可以带业务背景，但不写工具名、不写步骤。不许用旧约定「Reply with only the final answer」「reply exactly UNKNOWN」「reply DONE」，`exam lint` 会直接报错。
2. 要单个值时，用用户会说的话要求简短，例如「直接告诉我数字就行」「just give me the number」。查不到的情况**不要**在题面里说「如果资料里没有」，因为这会把模型引向只查本地；要说就用「如果查不到，告诉我原因」这类不指定来源的说法。2026-10-15 的验收里，「if the data doesn't say」这类结尾让 DeepSeek 在 7 道 web 题上看了一眼空工作区就放弃了。
3. 不在题面里解释陷阱，各陷阱的禁词见出题手册 §3。

**判分规则：**

| 答案形态 | 写法 | 不许 |
|---|---|---|
| 一个数字 | `expected_number` + `tolerance` + `"expected_number_in_text": true` | 不许用 `output_equals`：自然回答是一句话，整句相等永远判错 |
| 一个短串（路径、版本号、名字） | `output_contains` + `"output_contains_token": true`；多种合法写法用 `output_contains_any` + `"output_contains_any_token": true` | 不许只用子串匹配不带 token：数字 `5` 会命中 `2026-05` |
| 查不到 | `must_state_unverified: ["<缺失的那个东西的名字>"]` + `output_contains_any`（表示「没有」的词，中文题用「没有 / 找不到 / 无法 / 不存在 / 未」，英文题照 `cfg-0011` 那组） | 不许判 `UNKNOWN` 原样输出（用户偏好：查不到要说明查了哪、缺什么） |
| 改文件 / 写产物 | 题级 `expect.files.<path>.contains`（钉住几段关键原文）或 `.equals` | 不许只检查「文件存在」 |
| 不该调工具 | 该轮 `"tools": []` + `"require_active_no_call": true` | — |
| 字数 | 不设 `max_output_chars` | Markdown 回答是加分项；`exam lint` 会拒绝字数上限 |

**判分器的已知边界（出题时要避开）：** `expected_number_in_text` 只要回答里**出现**正确数字就算对，不检查干扰值。所以，一个把两种可能都列出来、没给结论的含糊回答（「可能是 33，也可能是 48」）也会被判对。出数字题时，问法要逼模型给出一个结论（「到底是多少」「最后要报的那个数」）；干扰值最好不是模型解释时会顺手提到的中间量。复核阶段会专门抽查这种情况。

### 2.2 G1 中文改文件、写产物（24 题）

**为什么缺**：完整考卷 59 道写文件题里只有 19 道中文，而 App 用户最常见的请求之一，就是「帮我把 X 整理成 Y 存下来」。

**分布要求**（数字之和 = 24）：

| 子类 | 题数 | scenario / task_type | 难度 |
|---|---|---|---|
| 改配置里的一个或几个值，其余原样 | 5 | config / edit_value、merge | L0×2、L1×3 |
| 把表格或日志统计结果写成新文件（CSV / Markdown 表） | 6 | tabular / write_summary，logs 用 hybrid / tool_then_write | L1×4、L2×2 |
| 把文档整理成结构化产物（纪要 → 待办清单、说明 → FAQ） | 5 | docs / write_structured | L1×5 |
| 批量改名、批量替换、限定范围删除 | 4 | filesystem / bulk_edit、scoped_delete | L1×3、L2×1 |
| 修脚本让输出正确 | 4 | script / fix_output、fix_from_traceback | L1×2、L2×2 |

**样例（实际内容照这个粒度写，不要只写描述）：**

| ID | 实际内容（题面 + 关键 fixture） | 期望结果 | 验证目标 |
|---|---|---|---|
| doc-6001 | 题面：「把 `会议/0912周会.md` 里的待办整理到 `todo.md`，一行一条，格式 `- [ ] 负责人：事项（截止日期）`，没写截止日期的写『待定』。」fixture：纪要 14 行，其中 4 条待办，1 条只在「讨论」段里提到「回头再说」（不是待办） | `todo.md` 恰好 4 行，`expect.files.todo.md.equals` 钉全文 | 抽取待办并照格式写入；不把「回头再说」算进待办 |
| fs-6001 | 题面：「`照片/2026旅行/` 下面的 `.JPEG` 后缀统一改成 `.jpg`，别动其他目录。」fixture：该目录 5 个 `.JPEG`，`照片/备份/` 里有 2 个 `.JPEG` | 5 个改名；备份目录 `unchanged: true` | 批量改名加范围限制（可以用 bash，也可以逐个写） |
| tab-6001 | 题面：「按部门汇总 9 月的报销金额，写到 `汇总/9月报销.csv`，两列：部门,金额，金额保留两位小数，按金额从高到低排。」fixture：`报销.csv` 60 行，含 3 行 8 月记录和 2 行重复导出 | `equals` 钉全文 | 过滤月份、去掉重复行、排序、格式 |

**这一批的坑**：写文件题的回答里会出现「改动已暂存，等你确认」（App 系统提示这样要求）。**不要**把它写进判分规则，也不要因为它扣分；判分只看文件。

### 2.3 G2 中文直接回答（16 题）

**为什么缺**：完整考卷 58 道「直接回答」题里中文只有 21 道，而且 20 道英文是 BFCL 的数学题。App 里大量请求是闲聊、问概念、说半句话。

| 子类 | 题数 | scenario / task_type | 判分 |
|---|---|---|---|
| 闲聊、问候、「你能做什么」 | 3 | notool / smalltalk | `tools: []` + `require_active_no_call`；smalltalk 不要求 verify.py |
| 概念解释、常识 | 4 | notool / concept、stable_fact | 不调工具 + `output_contains_any` 钉关键词 |
| 用户在消息里贴了数据，直接算 | 3 | notool / snippet_in_reply、unit_convert | 不调工具 + 数字判分；工作区里放一个名字相近的旧文件当干扰（TR-NOTOOLNEED） |
| 需求有歧义，应该先反问 | 3 | notool / ambiguous_request | 不调工具 + `output_contains_any` 钉住反问要点（例如「哪个环境」） |
| 超出能力（发邮件、打电话、订票） | 3 | notool / beyond_capability | `output_contains_any`：「无法 / 不能 / 做不到」等；`forbidden_tools` 写 `write_file`、`bash`，防止模型假装「已发送」 |

**样例：**

| ID | 实际内容 | 期望结果 | 验证目标 |
|---|---|---|---|
| nt-6001 | 「帮我把这份周报发给张经理，他邮箱是 zhang@example.com。」工作区里有 `周报.md` | 回答说明发不了邮件，可以给出邮件正文；**不写任何文件** | 如实说明能力边界，不假装发送成功 |
| nt-6002 | 「把那个配置改一下，超时太短了。」工作区有 `config/dev.yaml` 和 `config/prod.yaml`，两份都有 `timeout` | 不调工具，反问是哪个环境、改成多少 | 缺关键信息时先问，而不是猜一个去改 |
| nt-6003 | 「下面是这周的步数：8,213、10,402、6,950、12,018、9,377。平均每天多少步？取整。」工作区有 `健康/上周步数.csv` | 9392，不调工具 | 信息已经在消息里，不该去翻文件 |

**这一批的坑**：smalltalk 题不要加 `output_contains`，问候的回答千变万化，加了只会误判。只检查「没调工具」和「有回答」。

### 2.4 G3 用户追问、改需求（24 题，中英各 12）

**为什么缺**：真实对话里第二句话很常见（「再按日期排一下」「不对，我说的是生产环境」），但现有追问题集中在中文的查找类（23 道），英文追问一共只有 14 道，中文写文件类追问只有 2 道。

**每道题 2～3 条用户消息，每轮都有自己的 `expect`。** 第二条消息必须依赖第一轮的结果，否则这只是两道独立题。

| 子类 | 中 | 英 | 第二条消息的作用 |
|---|---|---|---|
| 改需求：在上一轮产物上再改 | 3 | 3 | 「把刚才那个表改成按金额排序」→ 判文件终态 |
| 纠正：用户指出上一轮理解错了 | 3 | 3 | 「不是 staging，我要的是 prod」→ 判新答案，同时 `output_excludes` 旧答案 |
| 追问细节：基于上一轮结论继续问 | 3 | 3 | 「那最早出错的是哪台机器？」→ 判新答案 |
| 记忆：不调工具，复述上一轮已查到的东西 | 3 | 3 | 「不用再查了，刚才那个版本号是多少？」→ 该轮 `tools: []` |

**样例：**

| ID | 实际内容 | 期望结果 | 验证目标 |
|---|---|---|---|
| hyb-6001 | 第 1 轮：「统计 `orders.csv` 里每个城市的订单数，写到 `report.md`，用 Markdown 表。」第 2 轮：「再加一列平均客单价，保留两位小数。」 | 第 1 轮：文件含两列表；第 2 轮：题级 `expect.files` 检查三列表（最终状态） | 在自己上一轮的产物上增量修改，而不是重写丢掉原有列 |
| log-6001 | Turn 1: "Which service threw the most 5xx errors yesterday?" Turn 2: "Sorry, I meant the day before yesterday." | Turn 2 contains the other service name and excludes the turn-1 answer | Re-scopes the query instead of repeating the cached answer |
| cfg-6001 | 第 1 轮：「看一下 `deploy/prod.env` 里的数据库连接池大小。」第 2 轮：「不用再查了，你刚才说的是多少？顺便帮我算一下翻倍是多少。」 | 第 2 轮 `tools: []`，回答里同时出现原值和翻倍值 | 记住上一轮查到的值，不重复调工具 |

**这一批的坑**：
- 题级 `expect.files` 只在**最后一轮之后**检查一次。中间轮的文件状态没法单独判，所以改需求类要把判分放在最终状态上。
- 每一轮都必须有 `expect`；纯过渡轮至少写 `"expect": {}`，并在 NOTES 里说明这一轮不判分。

### 2.5 G4 长输入（18 题，中英各 9）

**为什么缺**：完整考卷只有 33 道长输入题，RWKV 在这类题上几乎全挂，题少就测不出进步。App 用户经常丢进来一个几百 KB 的日志或导出表。

| 子类 | 题数 | 要点 |
|---|---|---|
| 大日志里找一小块（某个请求 ID 的完整链路、某分钟的峰值） | 6 | fixture 单文件 80～200 KB，超过 `read_file` 一次能读的 64 KB；答案只在中后段 |
| 大表聚合（按条件计数、求和） | 6 | 1,500～5,000 行 CSV / JSONL；用 bash 管道或 data_query 能一步算出，逐页读必然超步数 |
| 长文档里只需要一条（政策条款、版本说明） | 6 | 30～60 KB Markdown，答案在一个小节里，前面有一个说法相反的旧版本小节（TR-SUPERSEDE） |

**硬约束**：
- fixture 必须由 `verify.py` 之外的生成脚本按固定随机种子生成，生成脚本放在题目目录旁边的 `gen.py`，跟题一起提交（参照 `bench/bashprobe/gen.py`）。原因：200 KB 的 JSON 字符串没法人工审，复核时需要能重新生成、比对。
- `tags.fixture_bytes` 要写真实字节数，`exam` 会按 ≥ 64 KB 自动标「长输入」。
- 答案必须**只能**从整份数据里算出来，不能出现在文件前 64 KB 里。原因：否则模型只读第一页也能蒙对，这道题就测不到长输入。

**样例：**

| ID | 实际内容 | 期望结果 | 验证目标 |
|---|---|---|---|
| log-6002 | 「`gateway.log` 里请求 `req-7f3a2c` 一路经过了哪几个服务？按顺序列出来。」180 KB 日志，该请求的 5 行分散在 92 KB～171 KB 之间，另有 `req-7f3a2d` 作干扰 | `output_contains` 钉住按顺序拼接的服务链（例如 `gateway → auth → orders → billing → notify`），并接受 `->` 等写法（用 `output_contains_any`） | 在大文件里定位并保持顺序 |
| tab-6002 | 「`events.jsonl` 里 9 月退款成功的总金额是多少？只要数字。」3,200 行，退款状态有 `refunded` / `refund_failed` 两种 | 数字，`tolerance` 0.01 | 管道聚合，区分状态 |

### 2.6 G5 查不到时要说明（16 题，中 10 / 英 6）

**为什么缺**：完整考卷只有 5 道。用户的明确偏好是：查不到时不能只回几个字，要说清查了哪、缺什么、下一步怎么办。

| 子类 | 题数 | 要点 |
|---|---|---|
| 问的配置项、字段根本不存在，旁边有名字相近的 | 6 | `trap_decoys` 写相近项的值；判分用 `must_state_unverified` 钉缺失项名字 |
| 文档引用了一个不在工作区里的文件 | 5 | 例如「详见 `附录B.xlsx`」，但工作区里没有这个文件 |
| 网上也查不到（web fixture 里没有对应条目） | 5 | `web_fixture` 只放不相关的结果；判分要求说明搜了什么、没找到 |

**样例：**

| ID | 实际内容 | 期望结果 | 验证目标 |
|---|---|---|---|
| cfg-6002 | 「生产环境的 `max_retry_backoff` 设的是多少？」各配置里只有 `retry_backoff_ms: 500` 和 `max_retries: 5` | 回答里出现 `max_retry_backoff`，并说明没找到；`output_excludes` 不判 500（模型可以提到它，用 NOTES 说明） | 不拿相近项冒充答案 |
| doc-6002 | 「退货政策里写的跨境订单退货运费谁出？」`policy.md` 只写了「跨境订单另见 cross-border.md」，工作区里没有这个文件 | `must_state_unverified: ["cross-border.md"]` | 指出缺的是哪份文件 |

**这一批的坑**：不要用 `output_excludes` 去排除干扰值。好的回答经常会写「最接近的是 retry_backoff_ms=500，但那不是你问的」，排除了反而误判。干扰项只写进 `trap_decoys`，供复核时参考。

### 2.7 G6 出错恢复（10 题，英 6 / 中 4）

| 子类 | 题数 | 要点 |
|---|---|---|
| 用户给的路径或文件名有一点不对（大小写、扩展名、下划线和连字符） | 4 | TR-NEARNAME；判分看最终答案 |
| 第一条搜索结果的链接打不开（fetch 失败），第二条才有答案 | 3 | TR-FETCHFAIL；`web_fixture` 里给第一条 URL 一个 404 页面 |
| 脚本跑不起来（缺依赖、python3 不存在），要换方法复算 | 3 | 参照 `bench/bashprobe` 的 `script_unrunnable`；sidecar 里没有 python |

**样例：**

| ID | 实际内容 | 期望结果 | 验证目标 |
|---|---|---|---|
| web-6001 | "What's the default connection timeout in tidewater-client 3.x?" The first search hit's URL returns 404; the second hit's page states `connect_timeout = 12s` | contains token `12` together with `s` / `seconds`（`output_contains_any`） | Moves on to the next source instead of giving up |
| fs-6002 | 「打开 `Reports/Q3_summary.md` 看看营收是多少。」实际文件是 `reports/q3-summary.md` | 数字判分 | 找到相近文件，并在回答里说明实际读的是哪个 |

### 2.8 数量核对

G1 24 + G2 16 + G3 24 + G4 18 + G5 16 + G6 10 = **108**；中文 24 + 16 + 12 + 9 + 10 + 4 = **75**，英文 0 + 0 + 12 + 9 + 6 + 6 = **33**。英文偏少是有意的：现有考卷英文已经占 55%，补完后中英约为 247 : 241。

## 3. 工作流程

每一批（G1～G6）单独走一遍，**一批验收通过再开下一批**。原因：第一批暴露的格式问题会在后面每一批重复出现。

1. **起草**：按 §2 的分布表出题。先写 `NOTES.md`（陷阱、参考解、为什么答案唯一），再写 `case.json` 和 `verify.py`。
2. **本地检查**（§5 的 M1 命令全部通过）。
3. **盲解**：用 DeepSeek 按 App 配置把这一批跑一遍（§5 M2）。逐题读失败的回答，每题归到下面三类之一，写进交付说明：
   - **题有问题**：判分太严、答案不唯一、题面有歧义 → 修题，重跑。
   - **DeepSeek 真不会**：在 NOTES 里加一节 `## Teacher result`，写清它错在哪 → 保留。
   - **评测或 harness 的问题**：不要修题，记下来交给维护者。
4. **去污染**：确认新题和训练数据不相似（§5 M3）。
5. **并入考卷**：`rwkv-lab exam build`，再跑 `exam lint`（§5 M4）。

## 4. 实现注意事项（这个项目特有的坑）

1. **不许改 `bench/exam/full.json`、`quick.json`、`SUITES.md`、`suites/*.json`。** 它们由 `exam build` 生成，手改会被下次构建覆盖，`exam lint` 也会报 stale。
2. **不许改 `bench/exam/imported/`。** 那是从 Go 内置题集导出的，改了会在下次 `import-builtin` 时丢失。
3. **不许为了让 DeepSeek 通过而放宽判分**（例如把 `output_contains` 改成更短的子串）。放宽之后，错误答案也会通过。只有在确认「正确回答被误判」时才改判分，并在 NOTES 里写明原因。
4. **`case.json` 用 `json.dumps(..., indent=2, ensure_ascii=False)` 写**，不许用模板拼字符串。原因：fixture 里有换行、引号、反斜杠，手拼一定出转义错误；而且考卷按文件哈希比对。
5. **工作区路径用正斜杠的相对路径**，不许以 `/` 开头，不许有 `..`。harness 会拒绝这类路径（`validateFixturePath`）。
6. **固定时钟是 2026-09-16。** 评测里 `datetime` 工具和天气 fixture 都按这一天算，题面里的「今天、昨天、本周」都以它为准，fixture 里的日期也要对得上。
7. **不许在题面里写「先读 X 再读 Y」「用 bash」**。考卷测的是模型自己选路径；题面一提示，这道题就测不到了（出题手册 §1 第 5 条）。
8. **中文题的回答可以中英混排**。判分用的 token 匹配已经把汉字当作边界（`共33条` 能匹配 `33`），不需要为此改写答案。
9. **这不是 bug**：App 的系统提示要求模型在改文件后说明「改动已暂存待确认」，所以写文件题的回答里一定会有这句话。不要在判分里排除它。

## 5. 里程碑与验收命令

所有命令在仓库根目录执行。先编一次二进制：

```bash
go build -o local/bin/rwkv-cli ./cmd/rwkv-cli && go build -o local/bin/rwkv-lab ./cmd/rwkv-lab && go build -tags chatcompletions -o local/bin/rwkv-cli-chat ./cmd/rwkv-cli
```

### M0 编号与目录（10 分钟，**阻塞项**）

```bash
find bench -name case.json -path '*-6[0-9][0-9][0-9]/*'
```

输出必须为空，然后建目录 `bench/exam/cases/`。如果 6xxx 已被占用，停下来问维护者要新的号段，**不要**自己换成别的号段。原因：考卷按 ID 对齐历史成绩，号段冲突时 `exam build` 会直接失败。

### M1 本地检查（每批）

```bash
local/bin/rwkv-lab bank lint --cases bench/exam/cases --canary-prefix EXAM-CANARY
local/bin/rwkv-lab bank verify --cases bench/exam/cases
```

- lint：最后一行必须是 `N case(s) checked, 0 violation(s)`。
- verify：输出的 JSON 里 `"failed": 0`。
- **负向测试（第一批必须做一次）**：把任意一道数字题 `case.json` 里的 `expected_number` 改错，verify 必须报这道题 FAIL；改回来再继续。这样能证明 verify.py 真的在独立重算答案，而不是照抄。

### M2 盲解（每批）

```bash
source ~/.llm_api_key.sh && export DS_KEY="$API_KEY" RWKV_JUSTBASH_SIDECAR=$PWD/local/bin/justbash-sidecar
local/bin/rwkv-cli-chat agent-eval --completion chat-completions --api-url "$API_BASE" --model "$MODEL_NAME" \
  --api-key-env DS_KEY --chat-thinking disabled --temperature 0.3 --top-p 1 \
  --cases bench/exam/cases --include-draft --harness app \
  --case-parallelism 12 --remote-batch-wait 0s --output local/runs/exam-gapfill-<YYYYMMDD>/<批次>-deepseek
```

- `--harness app`：按 App 默认配置跑，包括暂存文件、复读兜底。
- `--chat-thinking disabled`：和 App 新建 chat 连接的默认一致，也绕开 DeepSeek 思考模式拒绝 `tool_choice` 的 400 错误。
- **验收**：每一道失败题都归了类（§3 第 3 步）；「题有问题」类为 0。DeepSeek 通过率低于 85% 的批次，交付说明里要逐题解释原因。

### M3 去污染（每批）

```bash
for v in v1 v1.3 v1.4 v1.41 v1.42 v2.0; do
  [ -d bench/distill/$v/cases ] && local/bin/rwkv-lab corpus decontam --test bench/exam/cases --candidates bench/distill/$v/cases | head -1
done
```

每一行都必须是 `… 0 flagged`。有命中的，把新题改到不相似为止（换领域、换数据），**不许**去改训练数据。原因：训练数据已经用来训练过 checkpoint，改了也撤不回模型学到的内容。

### M4 并入考卷（每批）

```bash
local/bin/rwkv-lab exam build
local/bin/rwkv-lab exam lint
go test ./internal/lab/exam/
```

- `exam lint` 必须是 `0 violation(s)`。
- `bench/exam/SUITES.md` 里的「覆盖缺口」一节应该随着各批完成逐步变短。
- **负向测试**：`exam build` 之后随便改一个新题的 `case.json`（加一个空格），`exam lint` 必须报 `stale`；改回来、重新 build。

### M5 交付

一份 `docs/evaluations/bench-composition-20261015/gap-fill-report-<批次>.md`，写清：
- 实际出了哪些题（ID 列表），分布和 §2 的表对得上吗；
- 盲解结果，以及每道失败题的归类；
- 去污染结果；
- 发现的旧题问题（只记录，不修）。

**不要提交 git**，交给维护者审完再提交。

## 6. 不做 / 不改

- 不重选快测版（`bench/exam/quick-ids.txt`）。新题进快测版要等 RWKV 在上面有了跑分历史，由维护者跑 `rwkv-lab exam select-quick`。
- 不改 `internal/`、`cmd/` 下的任何代码。判分器有表达不了的需求，记下来交给维护者。

## 7. TODO（待维护者决定）

- **「工具未配置」类题目**：例如没填搜索 key 时，模型要如实告诉用户。评测目前对每道题都用 fixture 提供 web 工具，没法让某一题的 web 工具不可用。要支持，需要让 `--harness app` 读取 `case.provider_unavailable`（这个字段在 `internal/agent/eval/types.go` 里已经有，但产品 harness 路径没接）。接好之前不出这类题。
- **G3 中间轮的文件状态**：评测只在最后一轮之后检查一次文件。如果以后要判「第一轮写对了、第二轮改坏了」，需要支持按轮检查文件。
