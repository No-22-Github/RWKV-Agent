# Prompt 格式、预填与思考

官方参照：`BlinkDL/RWKV-LM · RWKV-v7/RWKV7-G1x-templates.txt`；格式检查器 [Ai00-X/rwkv-prompt-format](https://github.com/Ai00-X/rwkv-prompt-format)。

## 1. 分词切法（World 词表 `rwkv_vocab_v20230424`，贪心最长匹配）

| 文本 | 切成 | 含义 |
| --- | --- | --- |
| `Assistant:` | `Ass` `istant` `:` | 冒号单独一个 token |
| `Assistant: Hello` | … `:` ` Hello` | 英文词**带前导空格**合成一个 token |
| `Assistant: 你好` | … `:` ` ` `你` `好` | 中文前的空格是**独立的** ` ` token |
| `Assistant: <think` | … `:` ` <` `think` | 空格并进 `<` |
| `Assistant: {` / `"` / ```` ``` ```` / `**` / `1` | ` {` / ` "` / ` ``` ` / ` **` / ` 1` | 空格都并进下一个符号 |
| `\n\n` | id 261 | 块分隔符是一个 token |
| `User` | id 24281 | 可当整数停止 token |
| `<think></think>` | `<` `think` `></` `think` `>` | `>` 和后面字符合并 |
| `<tool_call>{` | `<` `tool` `_` `call` `>{` | 同上 |
| `"name":"` | `"` `name` `":"` | 引号冒号引号是一个 token |

词表里**没有** `: `（冒号+空格）这个 token。token id 0 是 EOS。
需要核对时：拿词表文件写几十行贪心匹配脚本即可（不要用粗估器，粗估对英文高估约 35%、对中文和列表低估）。

## 2. 生成点：`Assistant:` 后面不留空格

训练里 `Assistant: Hello` 的第二个 token 是 ` Hello`。prompt 以 `Assistant: ` 结尾时，最后一个 token 变成孤立的 ` `，
模型被迫接一个"不带前导空格的 Hello"——训练里几乎没见过。G1L 实测（同题只差一个空格，贪心）：

- `What is the capital of France?` → 用中文回答
- `Write a haiku about rain.` → 输出 emoji 后自己续写 `User:`
- 整张考卷通过题约 −35%，英文题 97.8% 改用中文作答
- 中文题完全不受影响（中文前的空格本来就是独立 token）→ **只测中文会漏掉这个 bug**

## 3. 块结构

```
System: ...

User: ...

Assistant: ...

User: ...

Assistant:
```

- 块之间恰好一个 `\n\n`；块内**不能有空行**（模型把 `\n\n` 当"本块结束"）。
- 清洗 System/User 文本（官方做法），Assistant 文本是协议载荷不清洗：
  ```python
  re.sub(r'\n{2,}', '\n', txt.replace('\r\n', '\n')).strip()
  ```
- 标签区分大小写，后跟一个半角空格：`System:` `User:` `Assistant:`。`user:`、`User :`、全角冒号都算错。
- `System:` 只有一个，放最前面。
- **连续两条 User 不要合并**：比如"工具结果"和"本步提醒"分成两条 `User:` 块，合并成一条会明显掉分；提醒放前放后、有没有提醒影响都不大。

## 4. 预填（种子）的边界

预填 = 在 `Assistant:` 之后预先写一段，强迫模型走某种输出形状。规则：**种子的最后一个 token 在训练文本里也必须是独立 token。**

| 预填 | 结尾 token | 安全？ |
| --- | --- | --- |
| ```` ```json\n ```` | `\n` | 安全 |
| ```` ```json\n{"name":" ```` | `":"` | 安全 |
| `{"answer": `（带尾随空格） | ` ` | 安全，因为后面接 ` "` 类带空格 token |
| `根据上面的工具结果，` | `，` | 安全（中文标点独立） |
| `<tool_call>` | `>` | **不安全**，训练里是 `>{` |
| `<think></think>` | `>` | **不安全**，用 `<think></think` |

注意：预填写在 `Assistant:` 之后时，开头的空格是种子的一部分（` <think`、` ```json`），这和"生成点不留空格"不矛盾——
种子 ` <` 本身就是训练里的独立 token。解析输出时记得把种子拼回去。

### 锚点深度决定输出形状

- 浅锚点 ```` ```json\n ````：约一半调用把 arguments 写成字符串 `"arguments":"{\"query\":...}"`。
- 深锚点 ```` ```json\n{"name":" ````：字符串化降到 0；格式合规在 10k 上下文内基本无损，无锚点 5k–10k 就崩。
- 锚点拼写必须和指令/示例里逐字一致（紧凑写法冒号后无空格）；差一个空格合规率能从 ~99% 掉到 ~20%。
- **代价：深锚点堵死了"直接用文字回答"的出口**，模型宁可吐坏格式也不弃权。用深锚点就必须给一个 `no_tool` 之类的出口工具。
- 不加锚点、改用让模型自己写 `<tool_call>{…}</tool_call>` 信封也是可行路线（G1K/G1L 上闭合更积极、参数更完整、停止串不会与参数里的 ``` 冲突）。哪种更好随模型代际变，要实测。

### 短任务的抑制思考预填

压缩、抽取、分类这类一次性短调用，预填 ` <think></think`（假思考）。否则模型会自发进入思考跑偏，甚至幻觉"没有相关内容"。
实测抽取保留率 4/10 → 10/10。

## 5. 思考模式

| 写法 | 用途 |
| --- | --- |
| `Assistant: <think` | 完整思考 |
| `Assistant: <think></think` | 官方"假思考"：快 |

- 都**不带最后的 `>`**，让模型自己补；解析前把前缀放回去。`<think>\n</think` 已废弃。
- 控制思考长度：在用户文本**末尾**加 `(think)`、`(think a bit)` 或 `(think a lot)`，只加一个，小写半角。
- thinking=off 时 G1 也常自发写 `<think>`，上下文越长越频繁（500 token 时约 5%，10k 时约 75%）。解析器必须能剥掉思考块。
- 思考的原生形状：英文短思考，中位 200–340 字符；后续步会先总结上一步结果。英文题几乎全英文思考，中文题只有约 3 成用中文思考。
- 常见毛病：没写 `</think>` 就开始写调用（解析器要容忍）；思考里引用调用模板时会被 `</tool_call>` 停止串误切——
  若思考块未闭合且被切内容不是完整调用，把停止串补回去继续生成（最多几次）。
- 系统提示和每步提醒不能自相矛盾：开思考时提醒里别再写 "Do not open a <think> block"，改成 "Close your thinking with </think>, then output exactly one action."
- **预算**：开思考就要给足（决策 1024–4096 token）。16/96/512 token 的预算会把思考截在半句，测到的是 harness 不是模型。重试时不要把失控的思考回显。
- **基模当 Agent 要不要开思考：随模型变化，必须实测。** G1L 上开思考掉分（英文题掉、中文题持平）；G1K 正式版给足预算开完整思考反而涨。
- **空 think 不是中性前缀**：它暗示"已经想完了，现在行动"，会让模型更倾向直接调用工具、弃权变少。

## 6. 官方工具调用写法（参考）

```
System: Tools:
[
{"name":"find_free_slots","description":"…","arguments":{"date":{"type":"string"}}},
{"name":"create_calendar_event", …}
]
Return only a JSON function call.

User: Schedule a 30-minute sync with Bob on 2026-05-08 afternoon.

Assistant: ```json
{"name":"find_free_slots","arguments":{"date":"2026-05-08","duration_minutes":30}}
```

User: Function output:
{"free_slots":[…]}

Assistant:
```

官方原话 "The key is to keep it concise."。工具清单也可以写成函数签名列表 `- get_weather(location: string, unit?: "celsius" | "fahrenheit")`。
另一条可行路线是 Hermes 风格 `<tools>` 清单 + `<tool_call>` 信封 + `User: <tool_response>…</tool_response>`，详见 [agent-tools.md](agent-tools.md)。
**格式本身就是模型能力的一部分**：同一个 state-tuned 模型只把前缀从 ```` Assistant: ```json ```` 换成 `**Tool Call:**` 就会明显掉分。训练用什么格式，推理就逐字节用什么格式。
