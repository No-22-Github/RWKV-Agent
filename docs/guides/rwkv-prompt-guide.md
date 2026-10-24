# RWKV G1 系列 Prompt 经验

面向 RWKV-7 G1 系列（当前以 G1L 预览版 `rwkv-g1l-7b-temp-3797` 为准，G1K 的结论在每节注明）。
写给要给 RWKV 拼 prompt 的人：裸续写、Agent harness、训练数据渲染都适用。

RWKV 对 prompt 的字节非常敏感：多一个空格、少一个空行、大小写不对，接口不会报错，但输出会变差。
**检查的永远是真正发出去的字节**，不是脑子里的模板。

参照来源：

- 官方模板 `BlinkDL/RWKV-LM · RWKV-v7/RWKV7-G1x-templates.txt`
- [Ai00-X/rwkv-prompt-format](https://github.com/Ai00-X/rwkv-prompt-format)（格式检查器，规则与官方模板一致）
- 本仓库的实测：`docs/evaluations/g1l-prompt-format-20261024/`（本文的消融数据）及更早的评测报告

---

## 1. 分词器：先搞懂这几个切法

RWKV World 词表（`rwkv_vocab_v20230424`）是贪心最长匹配。和 prompt 格式相关的切法：

| 文本 | 切成 | 含义 |
| --- | --- | --- |
| `Assistant:` | `Ass` `istant` `:` | 冒号是单独的 token |
| `Assistant: Hello` | … `:` ` Hello` | 英文词**带前导空格**合成一个 token |
| `Assistant: 你好` | … `:` ` ` `你` `好` | 中文前的空格是**单独的** ` ` token |
| `Assistant: <think` | … `:` ` <` `think` | 空格和 `<` 合成 ` <` |
| `Assistant: ```json` | … `:` ` ``` ` `json` | 空格和反引号合成 |
| `Assistant: {` / `"` / `1` / `**` | … `:` ` {` / ` "` / ` 1` / ` **` | 同上，空格都并进下一个符号 |
| `\n\n` | 一个 token（id 261） | 块分隔符本身是一个 token |
| `User` | id 24281 | 可以当整数停止 token 用 |
| `<think></think>` | `<` `think` `></` `think` `>` | `>` 会和后面的字符合并 |
| `<tool_call>{` | `<` `tool` `_` `call` `>{` | 同上，`>` 和 `{` 合并 |
| `"name":"` | `"` `name` `":"` | 引号冒号引号是一个 token |

词表里**没有** `: ` 这个 token（只有 ` :`、`::`），所以 `Assistant:` 和后面的内容之间永远在冒号后断开。

复查方法：`third_party/rwkv-mobile/assets/rwkv_vocab_v20230424.txt` 加几十行贪心匹配脚本即可，
`rwkv-lab run cost` 回算 token 也用同一份词表。

## 2. 生成点：`Assistant:` 后面不留空格

**规则：prompt 以 `Assistant:` 结尾，冒号后什么都不加，让模型自己生成第一个 token。**

原因（见上表）：训练数据里 `Assistant: Hello` 的第二个 token 是 ` Hello`（带空格）。如果 prompt 以
`Assistant: `（带空格）结尾，最后一个 token 变成单独的 ` `，模型被迫接一个**不带前导空格**的 `Hello`——
这个组合在训练里几乎没出现过。

> 有一个细节和 rwkv-prompt-format 的说法不同：它写的是"`Assistant:`+`␠` 与 `Assistant`+`: ` 不是同一组 token"，
> 但词表里没有 `: `，真正的区别是"` ` + `Hello`"对"` Hello`"。结论一致。

中文不受影响：中文前的空格本来就是单独的 ` ` token，带不带空格切出来一样。所以这个错误在中文题上看不出来，
在英文、工具调用（` <`）、JSON（` {`）、代码块（` ``` `）上才会暴露。

G1L 实测（贪心，同一题只差一个空格）：

| 问题 | `Assistant:` | `Assistant: ` |
| --- | --- | --- |
| What is the capital of France? | ` The capital of France is Paris.` | `巴黎是法国的首都。`（英文题用中文答） |
| Write a haiku about rain. | ` <think>…`（正常进入思考） | `🌧️🌧️🌧️\nRaindrops fall…` 然后自己续写 `User:` |
| Give me three tips for learning Python. | ` 1. Practice…` | `<think>Okay…`（`<` 失去前导空格，思考块不规范） |
| Hi! How are you today? | ` I'm just a computer program…` | `👋 Hello!…` 然后续写下一轮 `User:` |
| 法国的首都是哪里？ | ` 法国的首都是巴黎。` | `法国的首都是巴黎。`（相同） |

完整考卷上的影响见 §7（`sp` 组）。

**例外：有意的种子。** 生成点后面可以接内容，只要接的是**训练里真实出现过的前缀**：
`Assistant: <think`、`Assistant: ```json`、`Assistant: {"answer": `（官方材料问答，这里的尾随空格是有意的，
因为 `": ` 后面接的是 ` "` 之类带空格的 token）。判断标准永远是：**种子的最后一个 token，在训练文本里是否也是一个独立 token**。

本仓库的现状（2026-10-24 核对）：Agent harness 和训练渲染全部以 `Assistant:` 或种子结尾；
唯一的裸 `Assistant: ` 在 BFCL 多轮路由阶段，已在 f1ab12f7 修掉。

## 3. 块结构

```
System: ...

User: ...

Assistant: ...

User: ...

Assistant:
```

- 块之间**恰好一个空行**（`\n\n`）。块内容里**不能有空行**——`\n\n` 是一个 token，模型把它当成"这一块结束"。
  官方建议先清洗 System/User 文本：`re.sub(r'\n{2,}', '\n', txt.replace('\r\n','\n')).strip()`
  （本仓库 `inference.CleanChatText` 做同样的事；Assistant 文本不清洗，因为它是协议载荷）。
- 标签区分大小写，后跟一个半角空格：`System:` `User:` `Assistant:`。全角冒号、`user:`、`User :` 都算错。
- `System:` 只有一个，放最前面。
- token id 0 是文档结束（EOS）。基模经常不发 EOS、直接续写下一轮 `User:`，所以停止条件要同时给
  `0` 和 `User`（id 24281）或文本停止串 `\n\nUser:`。本仓库评测用 `--api-stop-tokens 0,24281`。

## 4. 思考模式

只有三种合法写法（小写、逐字）：

| 写法 | 用途 |
| --- | --- |
| `Assistant: <think` | 完整思考 |
| `Assistant: <think></think` | 官方"假思考"：快、效果不错 |
| `Assistant: <think>\n</think` | 同上的另一种写法 |

注意都**不带最后的 `>`**：`></`、`>{`、`>\n` 会合成一个 token，把 `>` 写进 prompt 就把模型推到训练里没见过的边界。
本仓库 `inference.ThinkBlockFast/Full` 就是按这个规则扣下 `>`，输出后再补回。

控制思考长度：在用户文本**末尾**加 `(think)`、`(think a bit)`、`(think a lot)`（小写半角，只能一个）。

即使 thinking=off，G1 系列也常常自发写 `<think>`（G1K 正式版每步都写中文思考），解析器要能剥掉。

## 5. 工具调用：官方写法

官方模板的函数调用：

```
System: Tools:
[
{"name":"find_free_slots","description":"…","arguments":{"date":{"type":"string"}, …}},
{"name":"create_calendar_event", …}
]
Return only a JSON function call.

User: Schedule a 30-minute sync with Bob on 2026-05-08 afternoon.

Assistant: ```json
{"name":"find_free_slots","arguments":{"date":"2026-05-08","duration_minutes":30,"time_window":"afternoon"}}
```

User: Function output:
{"free_slots":[…]}

Assistant: ```json
```

要点：`System: Tools:` 是逐字前缀；工具清单可以是 JSON 数组（一行一个）或函数签名列表
（`- get_weather(location: string, unit?: "celsius" | "fahrenheit")`）；调用写在 ```` ```json ```` 围栏里；
结果以 `User: Function output:` 回传；**"The key is to keep it concise."**

本仓库默认的 `agent-wire-v1.0` 不是这个写法（`<tool_call>` 信封 + `<tools>` 清单 + `User: <tool_response>`，
沿用 Qwen3.6 的 Hermes 风格对齐），两者的对比见 §7。

## 6. 预填（prefill）的边界

把一段协议前缀预先写进 Assistant 回合，可以强迫模型走某种格式，但最后一个 token 必须是训练里的独立 token：

| 预填 | 结尾 token | 安全？ |
| --- | --- | --- |
| ```` ```json\n ```` | `\n` | 安全（训练里 `\n` 和 `{"` 分开） |
| ```` ```json\n{"name":" ```` | `":"` | 安全 |
| `<tool_call>` | `>` | **不安全**：训练里是 `>{`（`xml-route-v1` 的 envelope 预填有这个问题，默认预设不用） |
| `<think></think>` | `>` | **不安全**，要用 `<think></think` |
| `根据上面的工具结果，` | `，` | 安全（中文标点独立） |

---

## 7. G1L 消融结论（2026-10-24）

完整数据见 [G1L 消融报告](../evaluations/g1l-prompt-format-20261024/REPORT.md)。考卷 568 题、每组 2–4 遍、逐题配对加符号检验。

| 做法 | 效果 | 建议 |
| --- | --- | --- |
| 接受"先说一句话再调用"（`recover-preamble`） | +52 题 | **默认打开**。G1L 习惯先写"我先查一下……"再调用 |
| 生成点多一个空格 | −63 题，英文题 97.8% 变中文作答 | 绝对不要 |
| 快思考 `<think></think` / 完整思考 `<think` | −23 / −28 题 | 基模 Agent 不开思考 |
| 合并连续 User 消息（含"提醒前置"、"去掉提醒"两种变体） | −10 到 −17 题 | 工具结果和提醒分成两条 User |
| 去掉 `no_tool` 出口工具 | −12 题，重复调用 +30% | 保留，它是"结束出口" |
| 旧 ```` ```json ```` 围栏产品写法 | −68 题 | 不用 |
| 采样 `agent-fast`（T0.3 p0.5 presence0.5 freq0.1 decay0.996） | 最佳 | 默认 |
| 去掉重复惩罚 / 贪心 / T=1（含官方 demo 参数） | −12 到 −28 题 | 不用；惩罚不会损坏 JSON |
| 官方风格精简系统提示（`System: Tools:` 开头、两条规则、无示例） | 4 遍总分 +8.25（p=0.029）；直接作答 +28、本地读取 −13、外部信息 −9 | 改变的是调用倾向（更少调用），按产品取向选 |
| "不确定路径先 list_files" 提示 | 无效 | 不加 |

经验要点：

- **对 RWKV 改提示词，先看行为分布再看总分。** 精简提示与默认提示总分接近，但做对的是两批不同的题。
- **RWKV 会照抄自己上一回合。** 刚输出过 `<tool_call>` 的模型，下一步很容易原样再输出一次（首次重复中 56% 紧邻上一步）。
  提示词、提醒位置、采样都只能压低约 20%，需要训练数据示范"读到即答"。同理，作答阶段重试时不要把被拒的调用再放回上下文。
- **提示里的语言会带偏输出语言。** 尾随空格那组英文题全变中文；系统提示里固定拼入的中文说明，也可能拖累英文题（未单独测）。

## 8. 历史经验（G1K 及更早，仍可参考）

| 经验 | 来源 |
| --- | --- |
| 预填锚点的深度决定 `arguments` 形状：只预填 ```` ```json\n ```` 时约一半 `arguments` 写成字符串，预填到 `{"name":"` 时为 0 | 2026-08-28 G1I 探针 |
| 系统提示里的示例块是负资产；去掉示例 + 一阶段作答 + `no_tool` 出口，bfcl-product 40 → 49/60，请求字节 −56% | 2026-09-15 G1K wire 消融 |
| 带思考的模型要给足决策预算：路由 16 token、决策 512 token 会截断思考，测出来的是 harness 而不是模型 | 2026-08 / 2026-09-23 |
| `top_k=1` 时温度失效；截断（top_p）比温度更重要 | 2026-09-23 采样扫描 |
| 训练片段要从 `Assistant:` 之后开始，把空格划进训练片段，否则 ` <` 被拆开，与推理分词不一致 | 2026-10-03 v1.3 segments |
| 终答的训练片段必须带终止符，否则模型答完会续写 `✿text1✿` 或下一轮 `User:` | 2026-09-27 t927 复核 |
| 空搜索结果附一句中文说明（"同样的关键词再搜也不会有结果"）最好；英文 "tell the user…" 会被原样当成终答 | 2026-10-16 |
| 长网页：总结约 12K token 内健康；问事实时 6K 以后正确率掉到 2–4 成，后半页基本丢失 → 6K 截断 | 2026-10-20 |
| 基模不发 EOS、会续写下一轮，停止条件同时给 `0` 和 `User`（24281）或 `\n\nUser:` | 多次 |
| Hermes Agent 轨迹格式在 G1K 上 workbank 0/148：拿到结果后不写答案、一直调用 | 2026-10-03 |
