# RWKV-Agent × BFCL v4 A+B 组接入 —— 实施规格书 v3.1

> **交付对象:编码 Agent（CodeX / Claude Code）。** 读完这份文档应当能直接开始写 `internal/bfcl` 包,不需要回来问「题目从哪来」「result 长什么样」「基线怎么定」。
>
> 文中「必须」「不得」「不许」是硬约束,每条都附了理由。**理由不成立之前不要绕过。**
>
> **本文档合并并取代** `bfcl-matrix-design.md` 与早期版本的实施 spec。看到旧文档里的「vanilla / harness 双轨」「L0–L4 五档梯子」「XML envelope」,一律以本文档为准。
>
> **v3.1 变更:** 统一 5pp 噪声线作废,改配对检验(§9.1);抽样算法补齐可复现细节(§5.2–5.3);校准改为预注册(§5.4);增强档补齐完整定义(§2.2b);效率维度去掉「结构性优势」表述(§9.2);greedy 语义显式化(§2.2c)。
>
> **归档修订:** 补充 v1/v2 manifest 的最终选用规则;修正层内等间隔取样索引;删除「两档分数不得完全相同」这一不应预设结果的验收条件。
>
> **核心章节是 §3。** 它描述这个项目唯一不可再推导的东西:BFCL 的真实记录格式与判分语义。架构你可以自己想,判分语义你想不出来,猜错了整个评测结果无效。

---

## 0. 目标

把 BFCL v4 的 **A 组(Non-Live 静态单轮,1390 题)** 和 **B 组(Live 单轮,2251 题)** 接入 RWKV-Agent,共 3641 题,用抽样跑出一张 5 格矩阵,同时回答两个问题:

- **模型有多强?** —— 固定 harness,换模型
- **兜底值多少?** —— 固定模型,开关兜底

**关键取舍一:生成用我们自己的 harness,判分用官方 Python 判分器。** 不写 handler、不提 PR、不让官方 harness 驱动我们的模型。

**关键取舍二:不追求与公开榜单的绝对分对齐。** RWKV 与 transformer 架构血缘不同,绝对分横向比意义有限。本设计要的可比性是**内部可比**:同一工具协议、同一 harness、同一题集、同一判分,唯一变量分别是「模型」和「兜底开关」。

---

## 1. 总览

### 1.1 范围内的 split

| 组 | Split | 题数 | 有 ground truth | 判分方式 |
|---|---|---|---|---|
| A | `simple_python` | 400 | ✅ | AST |
| A | `simple_java` | 100 | ✅ | AST(Java 类型转换) |
| A | `simple_javascript` | 50 | ✅ | AST(JS 类型转换) |
| A | `multiple` | 200 | ✅ | AST |
| A | `parallel` | 200 | ✅ | AST(多调用) |
| A | `parallel_multiple` | 200 | ✅ | AST(多调用) |
| A | `irrelevance` | 240 | ❌ | 解码成功 = 失败 |
| B | `live_simple` | 258 | ✅ | AST |
| B | `live_multiple` | 1053 | ✅ | AST |
| B | `live_parallel` | 16 | ✅ | AST(多调用) |
| B | `live_parallel_multiple` | 24 | ✅ | AST(多调用) |
| B | `live_relevance` | 16 | ❌ | 解码失败 = 失败 |
| B | `live_irrelevance` | 884 | ❌ | 解码成功 = 失败 |

**A 组 1390,B 组 2251,合计 3641。** 实现完成后必须能打印出这三个数并与本表逐行对上;对不上说明有 split 漏读或多读。

### 1.2 明确不做什么

以下都是讨论后**否决**的方案。不要实现,也不要「顺便也支持一下」:

1. **不写 BFCL handler、不改上游 `model_config.py` 提 PR。** 一旦模型进了官方仓库,prompt 渲染权归官方,我们失去逐字节控制,而 RWKV 对 prompt 字节敏感是已实测事实。
2. **不起 OpenAI 兼容端点让 `bfcl generate` 驱动我们的模型。** 那样测的是「RWKV 在 gorilla 默认模板下的表现」,与产品无关。
3. **不用 Go 重写 AST 判分器。** 判分语义有大量反直觉细节(§3.3),重写必然产生微妙偏差,一旦偏差,用公开 benchmark 的全部意义(可比性)就归零了。
4. **不碰 `multi_turn_*` / `memory` / `web_search` / `format_sensitivity`。** 这四组需要状态模拟器、记忆后端、联网或格式模板,全部推迟。
5. **不使用 XML envelope 工具协议。** 已弃用,实测 Markdown 更稳定。任何一格都不得出现 XML 协议。
6. **不做 L0–L4 五档消融梯子。** 已压缩为两档(§2.2)。

### 1.3 版本固定

必须钉死并写进 `run.json` 的 manifest:

- 数据集仓库:`ShishirPatil/gorilla`,路径 `berkeley-function-call-leaderboard/bfcl_eval/data/`
- 记录 clone 时的 **commit SHA**(`git rev-parse HEAD`)
- 判分器:`pip install bfcl-eval==<版本>`,记录**精确版本号**

**理由:** BFCL 会随榜单更新增删题目、修改标准答案。不固定就没法复现,两次跑分的差可能来自数据集变动而不是模型。primitive-bench 我们已经因此做了 commit 快照,这次同理。

---

## 2. 评测矩阵

### 2.1 矩阵

| | **基线档**(无兜底) | **增强档**(兜底全开) |
|---|---|---|
| RWKV7-G1i 7.2B | | |
| Qwen3-8B(Markdown 协议) | | |
| Qwen3-8B(原生 FC,参考格) | — | |

共 5 格。

- **竖着读一列** → 固定 harness,不同模型 = **模型能力**
- **横着读一行** → 固定模型,开关兜底 = **兜底机制的价值**
- **第三行参考格** → 对照模型的最佳形态,用途见 §2.4

### 2.2 两档定义

两档的唯一差别是**兜底机制的开关**,其余(工具协议、渲染、采样、题集、判分)必须逐字节相同。

**基线档 —— 我们的框架,无兜底**

- 工具协议:**Markdown**(围栏 + JSON 参数体)
- 模型调用:**恰好 1 次**
- 解析:一次性,失败即判失败
- 采样:**greedy**(语义定义见 §2.2c,不得直接在配置里写 `temperature: 0.0`)

**增强档 —— 兜底全开**

在基线档基础上打开:格式修复、解析容错、重试、渐进式工具暴露、门控。**完整定义见 §2.2b —— 那一节不填完不许开跑。**

> **循环救援、子 Agent 委派不启用。** BFCL A+B 是单轮题,这些机制在这里没有发挥空间。**不许**为了让增强档好看而在单轮题里塞多轮机制。

### 2.2b 增强档的完整定义(**待填,阻塞项**)

下面每一项都必须有确定答案并写进 manifest。**留空的项编码 Agent 一定会自己填,而且填出来的东西无法复现、也无法跨版本比较。**

| 项 | 必须写清 | 取值 |
|---|---|---|
| 格式修复触发条件 | 什么样的输出算「格式坏了」 | **待填** |
| 格式修复的操作集 | 允许做哪些修补,逐条列出 | **待填** |
| retry 触发条件 | 解析失败?schema 非法?两者都算? | **待填** |
| schema 非法参数是否 retry | 是 / 否 | **待填** |
| retry prompt | 逐字节内容,含是否回传上一次的错误信息 | **待填** |
| retry 次数上限 | 整数 | **待填** |
| 每次调用 token 上限 | 整数 | **待填** |
| 渐进式工具暴露顺序 | 第一批暴露哪些、何时扩展、依据什么 | **待填** |
| 门控依据 | 判据是什么、阈值多少 | **待填** |
| router 调用是否计入上限 | 是 / 否 —— 影响 token 成本口径 | **待填** |

> **硬约束:兜底逻辑不得读取 ground truth 或 `possible_answer/`,不得读取题目 ID 的任何语义。**
>
> 理由:一旦兜底能看到答案,测到的就是 **evaluator rescue** 而不是 **harness fallback**,两档之差变成「我们能猜到答案」而不是「我们的框架能救回格式」。这是本设计最致命的一种污染,而且它非常容易在「让某道题过」的动机下悄悄发生(§7.3 第 11 条)。
>
> **实现约束:** `internal/bfcl` 包内,兜底代码路径不得 import 任何加载 `possible_answer/` 的模块。加载标准答案的函数放在独立包,由判分侧调用,兜底侧编译期就够不到。

### 2.2c greedy 语义(显式定义)

**不得在配置里直接写 `temperature: 0.0`。** 当前 `internal/continuation/continuation.go:76` 明确拒绝 `temperature <= 0`,YAML 里写 0 要么被拒、要么诱使实现者去改全局 continuation 语义 —— 后者会影响产品所有路径,代价远大于收益。

正确做法:

1. **manifest 层**记录语义而非数值:`sampling: {greedy: true, top_k: 1}`
2. **RWKV 适配器**在边界把 greedy 映射成该 provider 能接受的最小正温度 + `top_k=1`,并把**实际生效的数值**一并写进 manifest(`effective_temperature`)
3. **对照模型路径**记录它实际生效的参数(不同 API 对 `temperature=0` 的处理不同,以服务端回显或文档为准)
4. **不得**为此修改 `continuation.go` 的全局校验

**greedy 确定性自检(必做):** 在**真实并发度**下,把同一组 20 题跑两遍,输出必须**逐字节相同**。

> 理由:我们在 primitive-bench 上实测过,temp 0 下批大小不同会翻转刀尖上的 token。只做参数映射不足以保证确定性。自检不过 → 两档之差里混进了采样噪声,整张矩阵作废。

**这个切法测到的和测不到的**

测得到:**兜底机制的价值。**

测不到:**渲染层的价值** —— 渲染已经折进基线档了。渲染对 RWKV 的贡献很可能是全框架最大的一块(模板探测实验、primitive-bench 13/30→23/30 都指向这里),但本设计不量化它。

> **因此报告措辞必须是「兜底的价值」,不得写成「框架的价值」。** 想量化渲染,需要额外加一档官方 prompting 渲染的外部基线,那是后续的事,本轮不做。

### 2.3 两行走的是不同代码路径

RWKV 走**原生续写**,对照模型走 **Chat Completions**。这是两条不同的代码路径,prompt 组装方式根本不同。

- **共享的:** 工具调用协议(Markdown)、Agent 循环、解析层、兜底机制、判分器
- **不共享的:** prompt 组装 —— 对照模型拿到的是它自己的 chat template

> **报告里不得写「同一 prompt」,只能写「同一工具协议与同一 harness」。**

这个安排对对照模型是**更公平**的(它没被硬塞进 RWKV 的续写格式),所以不削弱结论。

### 2.4 协议偏置与参考格

对照模型仍被要求用 Markdown 工具协议而非它的原生 function calling。但 Markdown 围栏 + JSON 参数体是通用模型见过最多的形态,**强加的是一种常见格式,不是一套定制协议**,偏置远小于早期 XML 方案。

保留一个**参考格**把这点说死:对照模型用**原生 FC 模式**(`tools` 参数)+ 兜底全开,即它的最佳形态。三个数各自成立:

- 原生 FC = 对照模型真实水平的上界
- 走 Markdown 协议 = 控制了协议变量的对照
- RWKV 走 Markdown 协议 = 我们的成绩

**不得只报中间那个数。** 那会让我们看起来比实际更好,而且很容易被拆穿。

### 2.5 归因限制(硬约束)

**不得把两档 delta 的差异归因为架构。**

Qwen3-8B 有大量工具调用后训练和原生 FC 支持,g1i 是 preview checkpoint。**后训练弱的模型本来就更吃 scaffolding,与线性注意力还是 transformer 无关。** 两行矩阵无法把这两个因素拆开。

- ✅ 「g1i 在当前后训练水平下,兜底带来的增益显著大于 Qwen3-8B」
- ❌ 「因为 RWKV 是线性注意力,所以对 harness 的边际收益更高」

要支撑第二种说法,需加一行「同量级、工具后训练明显更弱的稠密模型」。**本轮不做。**

### 2.6 目标设定

**不预设「要跟 Qwen3-8B 打平」这类目标分。**

目标一旦锁定,选择压力会渗进 split 的取舍和抽样的种子,而且渗得自己都察觉不到。承诺的是**无论结果如何都完整报出整张表**。

---

## 3. BFCL 数据结构与判分契约(核心章节)

### 3.1 数据来源

```
仓库    ShishirPatil/gorilla
路径    berkeley-function-call-leaderboard/bfcl_eval/data/
题目    BFCL_v4_<category>.json                   ← JSONL,尽管扩展名是 .json
答案    possible_answer/BFCL_v4_<category>.json   ← 同样是 JSONL
```

**坑 1:文件扩展名是 `.json` 但内容是 JSONL(每行一个独立 JSON 对象)。** 不要整文件反序列化,必须逐行读。

**坑 2:文件末尾无换行符。** `wc -l` 会比实际记录数少 1(例如 `simple_python` 是 400 条但 `wc -l` 报 399)。按非空行计数,不要用 `wc -l` 做校验。

**坑 3:`irrelevance`、`live_irrelevance`、`live_relevance` 在 `possible_answer/` 下没有对应文件。** 这不是缺失,是设计 —— 这三个 split 不需要标准答案(见 §3.5)。加载器遇到这三个 split 不得报错。

### 3.2 题目记录格式

A/B 两组所有 split 共享同一 schema,恰好三个字段。真实记录(`simple_python_0`,逐字节照抄):

```json
{
  "id": "simple_python_0",
  "question": [[{"role": "user", "content": "Find the area of a triangle with a base of 10 units and height of 5 units."}]],
  "function": [
    {
      "name": "calculate_triangle_area",
      "description": "Calculate the area of a triangle given its base and height.",
      "parameters": {
        "type": "dict",
        "properties": {
          "base":   {"type": "integer", "description": "The base of the triangle."},
          "height": {"type": "integer", "description": "The height of the triangle."},
          "unit":   {"type": "string",  "description": "The unit of measure (defaults to 'units' if not specified)"}
        },
        "required": ["base", "height"]
      }
    }
  ]
}
```

#### 反直觉的地方(不写清楚,实现者会按常识写然后跑不通)

**a) `question` 是嵌套两层的列表,即使是单轮题。** 外层代表轮次,A+B 组的外层长度**恒为 1**(已对全部 3641 条校验过)。取用户消息必须 `question[0]`,不是 `question`。

**b) `parameters.type` 的值是 `"dict"`,不是 JSON Schema 标准的 `"object"`。** 同样,浮点写作 `"float"` 而不是 `"number"`,数组可能是 `"array"` 或 `"tuple"`。**不得把这些「修正」成标准 JSON Schema** —— 判分器按这套自定义类型名做类型检查,改了会导致渲染出的工具文档与判分器预期脱节。

**c) Live 组的 `question[0]` 里可能有 `role: "system"` 的消息。** 实测 `live_simple` 11 条、`live_multiple` 37 条含 system 消息。这是题目自带的业务 system prompt,必须原样注入,不得丢弃、不得与我们自己的 system prompt 拼接顺序搞反。**丢弃会导致这些题必然失败,且失败原因看起来像模型能力问题。**

真实样例(`live_simple_58-27-0`,注意 content 首尾都有换行、行尾有双空格):

```json
{"role": "system", "content": "\nYou are an AI chatbot who helps users in providing information related to movies, cinema halls and booking movie tickets for them.  \nAs a system bot, consider / calculate / default the movie date to current date (today's date) in India. \n"}
```

**不许 strip 这个 content。** 原文里的前后换行和行尾空格是题目的一部分。

**d) Live 组的 ID 不是连续整数,格式是 `live_<split>_<n>-<m>-<k>`**(如 `live_simple_0-0-0`、`live_multiple_1-0-1`)。ID 必须原样透传到 result 文件,**不得重编号、不得排序后重排** —— 判分器按 ID 匹配。

**e) `function` 数组长度差异极大。** `simple_*` 恒为 1;`multiple` 是 2–4;`live_multiple` **最多 37 个函数**。

**f) 工具文档体积会超预算。** 实测 `function` 字段序列化后的字符数:

| Split | p50 | p90 | max |
|---|---|---|---|
| `simple_python` | 524 | 693 | 1007 |
| `multiple` | 1351 | 2101 | 2813 |
| `parallel_multiple` | 1162 | 1877 | 2816 |
| `live_simple` | 663 | 1301 | 2261 |
| `live_multiple` | 3056 | 5741 | **21114** |
| `live_irrelevance` | 1663 | 4379 | **21114** |

21114 字符光工具文档就要占掉五六千 token,而 g1i 训练 ctx 是 12288 / 16384。**必须实现上下文预算保护**,见 §7.2。

**g) 有少量中文题目。** `live_irrelevance` 23 条、`live_simple` / `live_multiple` 各 5 条含中日韩字符。不是脏数据,不得过滤。

### 3.3 标准答案格式与判分语义 —— 全文最重要的一节

```json
{"id": "simple_python_0", "ground_truth": [{"calculate_triangle_area": {"base": [10], "height": [5], "unit": ["units", ""]}}]}
{"id": "simple_python_1", "ground_truth": [{"math.factorial": {"number": [5]}}]}
{"id": "simple_python_2", "ground_truth": [{"math.hypot": {"x": [4], "y": [5], "z": ["", 0]}}]}
{"id": "parallel_multiple_0", "ground_truth": [{"math_toolkit.sum_of_multiples": {"lower_limit": [1], "upper_limit": [1000], "multiples": [[3, 5]]}}, {"math_toolkit.product_of_primes": {"count": [5]}}]}
{"id": "simple_java_1", "ground_truth": [{"SQLCompletionAnalyzer.makeProposalsFromObject": {"object": ["Customers"], "useShortName": [true], "params": [{"limit": [50], "schemaFilter": ["public"]}]}}]}
```

结构:`ground_truth` 是**列表**,每个元素是一个**单键字典**(键 = 函数名),值是参数字典。**每个参数的值本身也是一个列表 —— 那是「可接受值的集合」,不是这个参数要传一个数组。**

`"multiples": [[3, 5]]` 表示:唯一可接受的值是数组 `[3, 5]`。外层那层列表是「可接受值集合」的包装。**这是最容易写错的一处。**

#### 判分语义(逐条核对自 `bfcl_eval/eval_checker/ast_eval/ast_checker.py`)

**S1 —— 空字符串 `""` 表示该参数可以省略。**
`"unit": ["units", ""]` = 要么不传 `unit`,要么传 `"units"`。

**S2 —— 反过来:possible_answer 里出现的参数,如果值列表里没有 `""`,那么必须提供,哪怕它不在 schema 的 `required` 里。**

最反直觉的一条,真实例子 `simple_python_5`:

- 函数 `solve_quadratic` 的 `required` 是 `["a", "b", "c"]`
- `root_type` 的描述明确写了 `Default value is 'real'`
- 但标准答案是 `{"a": [3], "b": [-11], "c": [-4], "root_type": ["all"]}` —— **没有 `""`**

所以模型**必须**显式输出 `root_type="all"`,只给 a/b/c 会判 `simple_function_checker:missing_optional`。

> **这不是 bug,不许「修正」标准答案。** 出题人的意图是「用户说了 find *all* the roots,模型应据此显式指定 root_type」。

**S3 —— 输出了 possible_answer 里没有的参数,直接失败**(`simple_function_checker:unexpected_param`),即使那个参数在 schema 里存在且值合理。「多传总比少传安全」的直觉在这里是错的,两个方向都会挂。

**S4 —— 字符串比较是宽松的,走 `standardize_string()`:删除空格和 `,./-_*^`,转小写,单引号转双引号。** 所以 `"April 1, 2024"` 和 `"April 1 2024"` 等价。**不要在我们这边再做一层 normalize** —— 判分器已经做了,我们多做一层只会掩盖真实失败模式,让 trace 与判分器实际看到的不一致。

**S5 —— Python 的 int→float 自动提升被允许**(期望 float 传 int 合法),反向不允许。

**S6 —— 嵌套字典的键走同一套:** 模型输出的 dict 里出现 possible_answer 中不存在的键 → `value_error:dict_key` 失败;possible_answer 中存在但模型没给、且值列表里没有 `""` → 同样失败。

**S7 —— `parallel*` 类别的多个调用不强制顺序**(判分器有 `parallel_function_checker_no_order`),但每个调用都必须能匹配上某个 ground truth 项,且数量要对得上。

### 3.4 result 文件契约 —— 我们要产出的东西

这是整个接入的接缝。Go 侧只负责产出这个文件,之后交给 `bfcl evaluate`。

**路径:** `<result_dir>/<model_dir_name>/**/BFCL_v4_<category>_result.json`

判分器用 `rglob("BFCL_v4_*_result.json")` 递归查找,**中间目录层级怎么命名不影响判分**。为与官方产物一致,建议 A 组放 `non_live/`,B 组放 `live/`。

**格式:** JSONL,每行一条。判分器只读两个字段:

```json
{"id": "simple_python_0", "result": "[calculate_triangle_area(base=10, height=5)]"}
```

其余字段(`input_token_count`、`latency` 等)会被原样带过,可以加,不影响判分。

#### `result` 字段的精确格式

**`result` 是一个字符串,内容是 Python 函数调用语法,外面套一层方括号。** 判分时的处理链:

1. `result.strip("`\n ")` —— 首尾的反引号、换行、空格被剥掉
2. 若不以 `[` 开头则自动补 `[`,不以 `]` 结尾则自动补 `]`
3. `ast.parse(cleaned, mode="eval")` —— 用 Python 的 AST 解析器解析
4. 顶层必须是一个 `ast.Call` 或元素全为 `ast.Call` 的列表,否则抛异常判失败

合法示例:

| 场景 | `result` 字符串 |
|---|---|
| 单调用 | `[calculate_triangle_area(base=10, height=5)]` |
| 带点号函数名 | `[math.factorial(number=5)]` |
| 多调用 | `[math_toolkit.sum_of_multiples(lower_limit=1, upper_limit=1000, multiples=[3, 5]), math_toolkit.product_of_primes(count=5)]` |
| 字符串参数 | `[get_movies(city='Mumbai')]` |
| 布尔参数 | `[github_star(repos='a,b', aligned=True)]` ← **Python 的 `True`,不是 JSON 的 `true`** |
| 无调用(irrelevance 期望) | 空字符串,或任何解析不出 Call 的文本 |

> **硬约束:布尔值必须写 `True`/`False`,空值必须写 `None`。**
> 理由:第 3 步用的是 Python `ast.parse`,JSON 字面量 `true`/`null` 会被解析成变量名(Name 节点)而不是常量,导致值比对失败。**这是最容易被漏掉的一条** —— 模型内部产出的是 JSON 参数体,序列化成这个字符串时必须做字面量转换。

**Java / JavaScript 类别例外:** `simple_java` / `simple_javascript` 的参数值在 result 里**一律写成字符串**,由判分器侧的 `java_type_converter` / `js_type_converter` 负责转型。判分器对这两个类别显式检查「值必须是 str,否则 `type_error:java`」。所以 `[SQLCompletionAnalyzer.makeProposalsFromObject(object='Customers', useShortName='true', params='{limit: 50, schemaFilter: public}')]` 这种形态才对。**嵌套结构的具体字符串写法,必须用一条真实题目验证过再铺开**(见 §8 M2 验收)。

### 3.5 relevance / irrelevance 的判分 —— 与 AST 完全不同

这三个 split **没有标准答案**,判分逻辑只有一条:**能不能从 `result` 解码出函数调用。**

| Split | 期望 | 判定 |
|---|---|---|
| `irrelevance` / `live_irrelevance` | 不该调用工具 | 解码**成功** → 失败(`irrelevance_error:decoder_success`) |
| `live_relevance` | 该调用工具 | 解码**失败** → 失败(`relevance_error:decoder_failed`) |

**空列表 `[]` 不算函数调用。**

> **统计陷阱:** A+B 全集里负样本共 `240 + 884 = 1124` 题,占 3641 的 **30.9%**。一个「永远不调用工具」的退化模型能在这 1124 题上拿满分,总平均直接超过 30%。
>
> **因此:不得输出一个总平均分作为主指标。** 报告必须逐 split 出分,并单独列出「正样本平均」与「负样本平均」两行。**这条是硬约束** —— 我们上一份报告已经因为方法论问题在群里被质疑过一次。

### 3.6 内部 case schema

我们仓库现有的 case 格式是 `schema_version: 3`。**不要把 BFCL 题目转换成 `schema_version: 3` 再跑。**

理由:`schema_version: 3` 是为 primitive-bench 那种「有工作区、有 fixture、有 max_turns、有 scorer」的多轮任务设计的,而 BFCL A+B 是纯单轮无环境的。硬套会引入不存在的概念,并让 Agent 循环跑起不必要的多轮,污染结果。

新建独立类型:

```go
// internal/bfcl/case.go
type Case struct {
    ID        string            // 原样透传,不得修改
    Category  string            // "simple_python" / "live_multiple" / ...
    Messages  []Message         // = question[0],含可能存在的 system 消息
    Functions []json.RawMessage // 原始工具文档,不做任何 schema 规范化
}

type Message struct {
    Role    string // "system" | "user"
    Content string // 不得 strip
}
```

`Functions` 必须保持 `json.RawMessage` 而不是解析成结构体,**理由见 §7.1**。

---

## 4. 前置校验:拿榜单给适配器做体检(必做,先于一切)

Chat Completions 适配器目前只用 DeepSeek 跑通过一轮,**未做 bug 排查**。这是整个横向对比最大的单点风险:适配器有 bug 通常不会崩,只会让对照模型的分数悄悄低几个点,而我们会把它读成模型差距。

**做法:**

1. 让对照模型走**原生 FC 模式**,跑 `simple_python` / `multiple` / `live_simple` 三个 split(约 900 题)
2. 与官方 BFCL 榜单上该模型的公开逐类别分对比。**跑之前从 gorilla 官方榜单页拉当前数值,不要用任何人记忆里的数字**

**判读:**

- 对得上(逐 split 差在个位数 pp 内)→ 适配器健康,后续对照数可信
- 差得多 → **是我们的适配器有问题,不是模型**。修完重验,不许带病往下走

> **这是本设计中唯一一处「与榜单可比」有用的地方:当体检,不当成绩。**
> 注意方向 —— 不是拿我们的分去够榜单,是拿榜单来验我们的管道。这个检查不做,后面所有对照数都建在流沙上。

**同时验:** 这一步顺带确认 DeepSeek 之外的模型也能走通该路径。

---

## 5. 抽样

全量 3641 题 × 5 格 = 18205 次调用,现阶段没必要。抽样跑矩阵。

### 5.1 为什么不能按 ID 等间隔取

BFCL 的 ID 不是随机序:`simple_*` 大致按贡献批次排列,`live_*` 的 ID 形如 `live_simple_<n>-<m>-<k>`,中间的 `m` 是来源簇编号。**按 ID 等间隔取会系统性偏向某些来源和主题簇**,抽样分数与全量分数的偏差不可控。

### 5.2 两维分层

两个维度都能直接从原始数据算出,不需要跑模型,且都与难度直接相关:

1. **工具个数**:`1` / `2–4` / `5+`
2. **工具文档长度**:按**该 split 内**的 p33 / p66 切三档(各 split 绝对长度差异极大,不能用全局阈值)

流程(每一步都必须是确定性的,不许有实现者自由裁量的余地):

1. split 内做两维笛卡尔积分层(最多 9 层)
2. **名额分配用最大余额法(largest remainder / Hare quota)**:先按占比取整数部分,余下名额按小数部分从大到小分配
3. **并列打破规则(固定)**:小数部分相同时,按「层的 key 元组升序」取前者,key = `(工具个数档序号, 长度档序号)`。不得用 map 遍历顺序、不得用随机数
4. **层内按 ID 自然序排序后取样**;第 `j` 个样本使用索引 `floor(j * 层大小 / 层名额)`,其中 `j=0..层名额-1`,不使用 `step=floor(层大小 / 层名额)` 的前缀取法
5. 空层(全集中该层为 0)跳过,其名额按上述最大余额法在剩余非空层中重新分配一轮

**ID 排序必须用自然序,不得用字典序。** `live_*` 的 ID 形如 `live_<split>_<n>-<m>-<k>`,字典序会把 `live_simple_10-0-0` 排在 `live_simple_2-0-0` 之前,层内等间隔取样直接偏掉。必须解析成三元组 `(n, m, k)` 做数值排序;`simple_*` 等解析成单个整数后缀。解析失败的 ID 视为错误并中止,**不得回退到字典序**。

**随机种子:** 本算法全程不使用随机数。配置里不设 seed —— 设了反而给人「换个 seed 再抽一次」的余地。

### 5.3 名额

| Split | 抽样数 | 说明 |
|---|---|---|
| `simple_python` | 40 | |
| `simple_java` | 20 | |
| `simple_javascript` | 15 | |
| `multiple` | 30 | |
| `parallel` | 30 | |
| `parallel_multiple` | 30 | |
| `irrelevance` | 30 | 负样本 |
| `live_simple` | 30 | |
| `live_multiple` | 40 | |
| `live_parallel` | 16 | 全取 |
| `live_parallel_multiple` | 24 | 全取 |
| `live_relevance` | 16 | 全取 |
| `live_irrelevance` | 30 | 负样本 |
| **合计** | **351** | 正样本 291 / 负样本 60 |

名额按**每 split 需要的分辨率**分配,不按全集占比 —— 因为报告是逐 split 出分的。**抽样集的总平均没有意义,不得报**(全集负样本占 30.9%,抽样集占 17.1%,两者本就不同口径)。

### 5.4 代表性诊断(预注册,不是验收门)

**顺序是硬约束:manifest 必须在任何模型跑之前生成并冻结。**

> ❌ **错误做法(v3 原文,已作废):**「跑完 Qwen,看哪个 split 偏差大,调名额/分层,重抽,直到全部 < 5pp」。
> 这是标准的 **outcome-guided sampling** —— 用结果反过来选样本。这样得到的抽样集在统计上不再是无偏的,而且这个操作从产物里看不出来,等于一个隐藏的自由度。

**正确流程:**

1. 按 §5.2–5.3 生成 manifest v1,写入 **SHA-256**,提交进仓库。**此时尚未跑过任何模型。**
2. 用 **Qwen3-8B** 在**增强档**下跑**全量 3641 题**,与 manifest v1 的 351 题逐 split 比对偏差。
3. **默认:偏差只报告,不回改。** 诊断结果原样写进最终报告。
4. **例外(唯一一次,机械触发):** 仅当某 split 的 `|抽样分 − 全量分|` **超过该 split 每题分辨率的 2 倍**时,按下方预写表格扩额,生成 manifest v2,再跑一次诊断,**之后无论结果如何都不再调整**。

| 触发条件 | 机械动作 |
|---|---|
| n ≤ 24 的 split 超标 | 该 split 改为全取 |
| 25 ≤ n ≤ 30 的 split 超标 | 名额 ×2 |
| n > 30 的 split 超标 | 名额 ×1.5,向上取整 |

**扩额动作中不得有任何人的判断** —— 不许「换个分层维度试试」「这个 split 的题目本来就怪」。要么按表格扩额,要么不动。

5. **manifest v1 和 v2 都保留在仓库里,最终报告必须同时给出两版的数。** 调整过这件事本身必须是公开可见的。未触发扩额时,五格矩阵统一使用 v1;触发扩额时,五格矩阵统一使用 v2,v1 仅作为诊断对照,不得混用两份清单跑矩阵。

**用对照模型而不是 RWKV 做诊断** —— 诊断的是题集代表性;用 RWKV 会引入「为了让自己的分好看而选题」的嫌疑。

**这个诊断能证明什么、不能证明什么(必须原样写进报告):**

- ✅ 「该抽样集对 **Qwen3-8B 在增强档下的表现** 具有代表性」
- ❌ 「该抽样集对所有模型、所有档位普遍具有代表性」

代表性是相对于某个具体模型和配置的性质。RWKV 的难度分布与 Qwen 不同(它在长上下文题上更吃亏),**抽样集对 RWKV 的代表性未经验证**。这是本设计已知且未消除的局限,不得略去不提。

### 5.5 冻结

- 抽样一次,存成 ID 清单文件**提交进仓库**,之后所有格子用同一份清单
- 不许每次重抽 —— 重抽的话跨格差异里会混进抽样噪声
- 清单文件的 hash 写进 `run.json` 的 manifest

### 5.6 每 split 的分辨率(逐 split 不同,不存在统一噪声线)

单题对应的百分点 = 100 / n。**各 split 差异极大,不得用一条统一阈值:**

| n | 单题 = | 代表 split |
|---|---|---|
| 40 | 2.50 pp | `simple_python`、`live_multiple` |
| 30 | 3.33 pp | `multiple`、`parallel`、`irrelevance` 等 |
| 24 | 4.17 pp | `live_parallel_multiple`(全取) |
| 20 | 5.00 pp | `simple_java` |
| 16 | 6.25 pp | `live_parallel`、`live_relevance`(全取) |
| 15 | 6.67 pp | `simple_javascript` |

统计处理见 **§9.1**。

### 5.7 成本

351 题 × 5 格 ≈ 1755 次调用,外加代表性校准的 3641 次和适配器体检的约 900 次。RWKV 7B 单流约 30 t/s、每次约 200 输出 token,两格约 40 分钟。

---

## 6. 接口契约

```go
package bfcl

// 加载。dataDir 指向 data/ 目录,逐行解析。
func LoadSplit(dataDir, category string) ([]Case, error)

// 抽样。读取冻结的 ID 清单,过滤。
func FilterBySampleList(cases []Case, listPath string) ([]Case, error)

// 渲染。tier 决定兜底开关;transport 决定走原生续写还是 Chat Completions。
func RenderPrompt(c Case, tier Tier, transport Transport) (string, error)

// 归一化 —— 本包最关键的函数。
// 把 Markdown 协议解析出的调用列表,转成 §3.4 定义的 Python 调用语法字符串。
func ToResultString(calls []ToolCall, lang Language) (string, error)

// 写出。按 category 分组写 BFCL_v4_<category>_result.json。
func WriteResults(resultDir, modelDirName string, entries []ResultEntry) error

type ResultEntry struct {
    ID     string `json:"id"`
    Result string `json:"result"`
    // 可选观测字段,不影响判分
    InputTokens  int     `json:"input_token_count,omitempty"`
    OutputTokens int     `json:"output_token_count,omitempty"`
    Latency      float64 `json:"latency,omitempty"`
    ModelCalls   int     `json:"model_calls,omitempty"`
}
```

### `ToResultString` 的「不得」清单

- **不得**输出 JSON 字面量 `true` / `false` / `null` —— 必须是 `True` / `False` / `None`(理由:§3.4,判分器用 Python `ast.parse`)
- **不得**对参数值做 trim / 大小写归一 / 标点归一(理由:§3.3 S4,判分器已经做了,我们再做一层会让 trace 与判分脱节)
- **不得**因为「schema 里这个参数是 optional」就省略模型给出的参数,也**不得**补全模型没给的参数(理由:§3.3 S2/S3,两个方向都会挂,且掩盖真实失败模式)
- **不得**在解析失败时回退成「输出空字符串」以外的任何东西。解析失败对 irrelevance 是**正确结果**,静默兜底会把 1124 题的分数变成假的

### 需要接入的既有符号(TODO —— 实现者在仓库里定位后填写)

- **待填**:Markdown 工具协议解析器的入口函数名与签名
- **待填**:本地原生续写 provider 的单次调用入口
- **待填**:Chat Completions provider 的入口,以及「原生 FC 模式」的开关位置(§2.4 参考格要用)
- **待填**:`run.json` / `trace.jsonl` / `summary.json` 的写出函数,本包复用而不是新写一套

---

## 6b. 配置

`configs/bfcl.yaml`:

```yaml
bfcl:
  # 版本固定 —— 三项必须与 run.json manifest 一致,不许只改一处
  data_dir: "third_party/gorilla/berkeley-function-call-leaderboard/bfcl_eval/data"
  data_commit: "待 M0 填写"        # git rev-parse HEAD
  evaluator_version: "待 M0 填写"  # pip show bfcl-eval | grep Version

  # 判分器侧
  result_dir: "runs/bfcl/result"
  score_dir:  "runs/bfcl/score"
  model_dir_name: "待 M0 填写"     # bfcl evaluate --model 传的值,见 §8 M0

  # 抽样
  sample_manifest: "configs/bfcl-sample-v1.json"
  sample_manifest_sha256: "待 M3 填写"

  # 上下文预算保护(§7.2 第 4 条)
  max_prompt_chars: 40000          # 超过则跳过并计入 skipped,不得截断

  # 采样 —— 五格都用这组,不许改。
  # 注意:不写 temperature,greedy 的数值映射在适配器边界做,见 §2.2c
  greedy: true
  top_k: 1
  max_tokens: 1024

  # 增强档兜底参数 —— 逐项见 §2.2b,全部待填
  fallback:
    retry_max: "待填"
    retry_token_limit: "待填"
    router_counts_toward_limit: "待填"

  splits:
    non_live: [simple_python, simple_java, simple_javascript, multiple, parallel, parallel_multiple, irrelevance]
    live:     [live_simple, live_multiple, live_parallel, live_parallel_multiple, live_relevance, live_irrelevance]
```

**`greedy`、`top_k`、`max_tokens` 不许动。** 确定性解码是复现性的前提;3641 道题的规模下,非贪心的方差会淹没两档之间的差值。

---

## 7. 实现注意事项

### 7.1 加载层

1. **`Functions` 保持 `json.RawMessage`。** 一旦解析成 Go 结构体再序列化回去,字段顺序、数字格式(`10` vs `10.0`)、Unicode 转义都可能变。RWKV 对 prompt 字节敏感,这种变化会静默改变分数且极难归因。
2. **JSON 解析必须用 `json.Decoder` 并开启 `UseNumber()`。** 否则 Go 会把所有数字变成 `float64`,`10` 渲染成 `10` 还是 `1e+01` 取决于格式化路径。
3. 不得对题目做任何过滤(中文题、超长题都不许跳过;超长题的处理见 7.2)。

### 7.2 运行层

4. **上下文预算保护:prompt 渲染后超过 `max_prompt_chars` 的题,跳过并记入 `skipped`,不得截断工具文档。** 截断会产生一个「看起来跑了但工具文档不完整」的结果,比不跑更有害。`skipped` 数必须出现在 summary 和最终报告里。
5. **基线档严格 1 次模型调用**(§2.2)。如果实现出来基线档也会重试,两档的差就不再是兜底的贡献量,整个设计失效。
6. **每题独立上下文,不复用 State。** BFCL A+B 是单轮题,题与题之间不得有任何状态延续。
7. **五格必须用完全相同的并发度跑**,并把并发度写进 manifest。我们在 primitive-bench 上实测过:temp 0 下批大小不同会翻转刀尖上的 token。

### 7.3 归一化层(最容易悄悄搞砸的地方)

8. **不许用 `fmt.Sprintf("%v", value)` 生成参数值。** Go 的 `%v` 对 bool 输出小写 `true`(Python 不认),对 float 可能输出科学计数法,对 nil 输出 `<nil>`。必须写显式的 `pythonLiteral(v any) string`。
9. **不许用模板引擎生成 result 字符串。** 参数值里可能含引号、反斜杠、换行,模板引擎的转义规则和 Python 字面量规则不一致。手写序列化,字符串值用 Python 转义规则。
10. **不许「顺手」`strings.TrimSpace()` 参数值**(§3.3 S4)。
11. **不许为了让某道题过而加兜底逻辑。** 典型诱惑:发现 `simple_python_5` 因为缺 `root_type` 挂了,于是加一条「schema 里有 default 就自动补上」。这会让这道题过,同时让所有 S1 类的题挂掉,净效果是负的。

### 7.4 判分层

12. **判分只调官方 `bfcl evaluate`,不得在 Go 里实现任何判分逻辑,包括「预检查」。** 一个 Go 侧预检查一旦和官方判分器不一致,就会产生两个互相矛盾的分数,而人会倾向于相信先看到的那个。
13. **`--partial-eval` 只在确实只跑了子集时才加**(抽样跑矩阵时必须加,全量校准时不许加)。官方文档明确说加了这个标记的分数可能与全集不一致。
14. **`underscore_to_dot` 必须为 false。** 这是判分器侧的一个开关,为 true 时会把函数名里的 `.` 换成 `_`。BFCL 有大量带点号的函数名(`math.factorial`、`geometry.area_circle`),设错会让这些题全挂,且错误信息表现为「函数名不匹配」,极易误判成模型问题。

### 7.5 通用

15. **`run.json` 的 manifest 必须同时记录:** 数据 commit、`bfcl-eval` 版本、格位(模型 × 档位 × transport)、并发度、`sampling: {greedy, top_k, effective_temperature}`、§2.2b 表格里的全部兜底参数、抽样 manifest 版本号与 SHA-256、`skipped` 列表、硬件型号与 serving 配置。缺任何一项这次跑分就不可复现。
16. 不许把 gorilla 整个仓库提交进我们的仓库。用 submodule 固定 commit,或写 `scripts/fetch-bfcl.sh` 按 commit 拉取。
17. **兜底代码路径不得 import 加载 `possible_answer/` 的模块**(§2.2b)。建议在 CI 里加一条依赖检查,而不是靠自觉。
18. **不得为了让 `temperature=0` 生效而修改 `internal/continuation/continuation.go`**(§2.2c)。映射在 BFCL 适配器边界做。

---

## 8. 里程碑

### M0 —— 版本固定与判分入口确认(0.5 天,无需 GPU,**阻塞项**)

1. clone gorilla,记录 commit SHA;`pip install bfcl-eval`,记录版本号。
2. **确认 `bfcl evaluate --model X` 的 X 必须是判分器包内 `model_config.py` 已注册的名字。** 判分器内部会 `get_handler(model_name)` 来拿 `decode_ast`。我们不提 PR,所以二选一,需人拍板:
   - **选项 A(推荐)**:加入一个只实现 `decode_ast`/`decode_execute`(直接继承 `base_oss_handler` 默认实现)、从不做推理的本地 stub handler + 一条 `model_config.py` 条目,约 20 行。可将 evaluator vendor 到 `third_party/`,也可在隔离的本地进程内注册 mapping;两者都必须固定 evaluator 版本且不修改上游。**注意这与 §1.2 否决的「写 handler 提 PR」不是一回事** —— 这是本地 decode-only stub,不进上游、不承担推理。
   - **选项 B**:直接复用一个已注册的 prompting 模式 OSS 模型名写 result。零改动,但 score CSV 会挂在别人的模型名下,半年后没人看得懂。

**验收:**
```bash
grep -E "data_commit|evaluator_version|model_dir_name" configs/bfcl.yaml
# 三项都不含"待 M0 填写"
```

### M1 —— 适配器体检(0.5 天,**阻塞项**)

执行 §4。**不通过不许进 M2。**

**验收:** 三个 split 的分数与官方榜单公开值逐项比对结果写进 `runs/bfcl/adapter-health.md`,含拉取榜单数值的日期和 URL。

### M2 —— 闭环打通,只跑 `simple_python` 全量 400 题(1 天)

实现 `LoadSplit` / `RenderPrompt` / `ToResultString` / `WriteResults`,只接一个 split,只跑基线档。

```bash
./dist/rwkv-cli bfcl-eval \
  --model /path/to/rwkv7-g1i-7.2b.pth \
  --split simple_python --tier baseline \
  --output runs/bfcl/m2-smoke

bfcl evaluate --model <model_dir_name> --test-category simple_python
```

**验收(正向):** `score/<model>/BFCL_v4_simple_python_score.json` 生成,`accuracy` 是 0–1 实数,`total_count` == 400。

**验收(负向,三条,缺一不可):**

1. 手工把某条正确 result 的一个参数名改错(`base=` → `bases=`),重跑 `bfcl evaluate`,**必须**失败且 `error_type` 为 `simple_function_checker:unexpected_param`。
2. 手工把 `simple_python_5` 的 result 里的 `root_type='all'` 删掉,**必须**失败且 `error_type` 为 `simple_function_checker:missing_optional`。这条专门验证 §3.3 S2 那个反直觉语义确实生效 —— 如果它居然通过了,说明 result 没被真正判分(多半是 ID 对不上导致条目被静默跳过)。
3. 手工把某条 result 的 `True` 改成 `true`,**必须**失败。验证 §3.4 的 Python 字面量约束是真的。

> **M2 的意义就是这三条负向测试。** 正向的 accuracy 是多少无所谓,此刻它只是个数字。

### M3 —— 抽样冻结与代表性诊断(1 天)

实现 §5.2–5.3 分层与最大余额分配,产出 manifest v1 并写入 SHA-256 提交 —— **必须先于任何模型跑**。随后执行 §5.4 诊断。

**验收(正向):** manifest v1 已提交且 SHA-256 记录在案;`runs/bfcl/sampling-diagnostic.md` 记录逐 split 的抽样分 vs 全量分,以及是否触发过机械扩额;若触发,v1/v2 两份 manifest 均在仓库中。

**验收(负向,两条):**

1. 用同一份数据、同一份代码重跑抽样,产出的 ID 清单 SHA-256 **必须与 v1 完全一致**。不一致说明算法里还有非确定性(map 遍历顺序、字典序排序、隐藏随机数)。
2. 手工构造一个 `live_simple_10-0-0` / `live_simple_2-0-0` 的排序用例,**必须**排成 2 在前、10 在后。排反说明用了字典序(§5.2)。

### M4 —— 跑满矩阵(1–2 天)

五格全跑。加载题数必须打印并与常量比对:A 组 `400+100+50+200+200+200+240 = 1390`,B 组 `258+1053+16+24+16+884 = 2251`,抽样后 351。

**验收:**
- **greedy 确定性自检通过**(§2.2c):真实并发度下同 20 题跑两遍逐字节相同
- 五格产物齐全,manifest 字段完整(§7.5 第 15 条)
- **必须用 trace/manifest 和 fixture 验证兜底开关确实走了不同代码路径**;两档分数完全相同是允许的,应如实报告 `delta=0`,不得为了制造差异修改样本或判分逻辑
- `skipped` 计数被打印且每题有明确原因;`live_multiple` 里含 37 个函数的那条题要么正常跑完、要么明确出现在 skipped 列表,不许静默消失

### M5 —— 报告(0.5 天)

产出 `docs/evaluations/bfcl-v4-ab-<日期>.md`,内容见 §9,措辞受 §10 约束。

---

## 9. 每格的产出与统计口径

### 9.1 分数怎么报、怎么检验

**每个 split 必须报原始计数,不只是百分比:** `correct/total`,以及基线→增强的**原始 delta**(题数与百分点各一)。

**两档比较用 McNemar 精确检验,不用两独立样本检验。** 两档跑的是**同一批题**,是配对二元数据:

- 只看不一致对:`b` = 基线对/增强错,`c` = 基线错/增强对
- 对 `min(b,c)` 在 `n=b+c`、`p=0.5` 下做精确二项检验
- 配对设计比独立比较省样本,这是本设计能在小样本上说话的唯一依据

区间估计可以另外做 paired bootstrap(按题重采样,保持配对),但**主检验以 McNemar 精确检验为准**,报告里给出 `b`、`c`、`p`。

**以下三个 split 标为「仅描述,不做推断」,只报 correct/total,不给 p 值:**

| Split | n | 单题 |
|---|---|---|
| `live_parallel` | 16 | 6.25 pp |
| `live_relevance` | 16 | 6.25 pp |
| `live_parallel_multiple` | 24 | 4.17 pp |

> 理由:这个量级下任何检验都没有推断力。给它们套 p 值不是严谨,是**装作严谨** —— 而且一旦被人指出来,会连带拉低整份报告的可信度。

**跨 split 汇总的检验:** 如需一个整体结论,在**正样本 291 题**上做一次 McNemar,单独报;**不得**把负样本混进来(拒调倾向与调用正确性是两种能力,合并后 p 值无法解释)。

**多重比较:** 逐 split 报了 10 个 p 值,必须声明未做多重比较校正,或对主结论用 Holm 校正。不得挑出最显著的那个 split 单独宣传。

### 9.2 每格必须记录的字段

1. **逐 split 分数**:`correct/total` + 百分比,13 行,外加「正样本平均」「负样本平均」两行
2. **失败类型分布,标注归属层:**

| 失败类型 | 归属 | 该谁修 |
|---|---|---|
| 解析不出调用 | 解析 / 兜底 | 框架 |
| 超上下文被跳过 | 上下文组织 | 框架 |
| 函数名选错 | 模型 | 训练侧 |
| 必填参数缺失 | 模型 | 训练侧 |
| 参数值错 | 模型 | 训练侧 |
| 多传了参数 | 模型 | 训练侧 |
| 该调不调 / 不该调却调 | 模型 | 训练侧 |

3. **效率维度(需观测,不预设结论):**

| 指标 | 单位 | 跨模型可比性 |
|---|---|---|
| prompt 字节数 | bytes | ✅ 可比 —— tokenizer 无关 |
| 输入 token 数 | tokens | ❌ **不可比** —— 两个模型 tokenizer 不同 |
| 输出 token 数 | tokens | ❌ **不可比** —— 同上 |
| 模型调用次数 | 次 | ✅ 可比 |
| 墙钟延迟 | 秒 | ⚠️ 仅在同硬件同服务配置下可比,**必须连硬件型号与 serving 配置一起记** |
| 峰值内存 | MB | ⚠️ **仅本地路径可得**;对照模型走 API 时填 `N/A`,不得用本地 Qwen 的数顶替 |

> **不得把 token 数当成同一口径的成本做横向比较。** 两个模型的 tokenizer 和 prompt 组装路径都不同,同一道题的 token 数差异里混着分词粒度差异,不是效率差异。要做成本比较,**跨模型用字节数和调用次数,token 数只在同一模型的两档之间比**。
>
> **也不得预先把效率写成「RWKV 的结构性优势」。** 那是待验证的假设,不是已知前提 —— 和 §2.6 不预设目标分是同一条纪律。报告里只陈述观测值。

第 2 项在当前阶段比分数更有用 —— 框架还是半成品,分数下周就变了,**失败分布告诉你下周该改哪一层**。半成品阶段需要的是工作队列,不是成绩单。

第 3 项**必须和 accuracy 并列进 summary,不放附录**,但措辞受上面两条约束。

---

## 10. 对外表述

**可以声称:**

- 同一工具协议、同一 harness、同一题集、同一判分下,g1i 7.2B 与 Qwen3-8B 的逐 split 对比
- 兜底机制的增量贡献(基线档 → 增强档的差值)
- 各模型的调用次数与 prompt 字节数对比(§9.2 中标 ✅ 的维度)
- 失败模式的分类统计

**不得声称:**

- **不得**说本表任何数字与 BFCL 官方榜单可比 —— 生成阶段用的是我们自己的协议和 harness。§4 的适配器体检是例外,但那是校验管道,不是本表的成绩
- **不得**用总平均分做横向比较,也不得报抽样集的总平均(§5.3)
- **不得**把两档 delta 的差异归因为架构(§2.5)
- **不得**把本设计测到的东西说成「框架的价值」,只能说「兜底的价值」(§2.2)
- **不得**只报「Qwen 走 Markdown 协议」那一个对照数而不报参考格(§2.4)
- **不得**用统一噪声线解读 delta,也不得给 `live_parallel` / `live_relevance` / `live_parallel_multiple` 三个 split 附 p 值(§9.1)
- **不得**把 token 数当成跨模型可比的成本,**不得**把效率写成「RWKV 的结构性优势」(§9.2)
- **不得**声称抽样集对 RWKV 具有代表性 —— 诊断只在 Qwen 增强档下做过(§5.4)
- **不得**在未声明多重比较处理的情况下挑出最显著的 split 单独宣传(§9.1)
- **不得**写「同一 prompt」,只能写「同一工具协议与同一 harness」(§2.3)

---

## 11. 与既有题集的关系

- **回归集**:现有 94 道(boundary / smoke / assistant / primitive×2)。小、快、每次提交都跑,只防退化,**不进本矩阵**。
- **诊断集**:本矩阵(BFCL A+B 抽样 351 题)。慢,里程碑级跑一次,用来找方向。

两者不许混报。回归集分数上升不代表能力提升 —— 它有 78/94 道同源于 primitive-bench。

---

## 12. 版本语义

`manifest.harness.bfcl_adapter_version`,形如 `bfcl-ab-v1`:

- **major**:工具协议变更、渲染变更、归一化规则变更、两档定义变更、抽样清单变更 —— 与旧版分数不可比
- **minor**:新增 split、新增统计维度 —— 旧分数仍可比
- **patch**:修 bug、改日志 —— 分数应当不变,若变了说明是 major

**数据集 commit 或 `bfcl-eval` 版本变更,一律按 major 处理**,即使代码没动。

---

## 13. 待决策清单

动手前需要人拍板:

1. **§2.2b 增强档定义表格的全部 10 项** —— **阻塞项**。留空则实现者自行发挥,结果不可复现也不可跨版本比较
2. **判分入口用选项 A 还是 B**(§8 M0)—— **阻塞项**
3. **§5.4 的调整规则** —— 采用本文档的「预注册 + 唯一一次机械扩额」,还是更宽的「最多一次人工调整」。前者更严,后者更灵活;选后者的话调整优先级与停止条件必须同样预先写死
4. **对照模型走本地 vLLM 还是 API** —— 走 API 要确认服务端没做量化;且峰值内存一栏将为 `N/A`(§9.2)
5. **参考格用对照模型的哪种原生形态** —— 原生 FC(`tools` 参数),还是官方推荐的 prompting 模板。选定后把渲染出的完整 prompt 存进 `runs/.../native_prompt_sample.txt` 备查
6. **`max_prompt_chars` 取值** —— 默认建议 40000,需结合 g1i 实际 ctx 与对照模型 ctx 取小者
7. **多重比较是否做 Holm 校正**(§9.1)—— 做则主结论更稳,不做则必须在报告里明确声明未校正
8. **「7B 在 Markdown 下比 13B 稳」这个结论要不要写进报告** —— 早期探针数据(`**Tool Call:**` → `### Tool Output`:13.3B 16/20、7.2B 17/20)显示两个尺寸基本打平,1 例之差不显著。若新结论仍是 20 样本量级,建议降级为「两个尺寸在 Markdown 下表现相当,均优于 XML」—— 这句现有数据就能支撑,且已足够说明换格式是对的。要保留原结论,需先把样本量拉到能撑住它的规模
