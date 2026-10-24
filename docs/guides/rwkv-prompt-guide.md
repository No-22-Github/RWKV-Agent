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

## 7. G1L 消融结果（2026-10-24）

（跑分进行中，结果填入此节。）

## 8. 历史经验（G1K 及更早，仍可参考）

（整理中。）
