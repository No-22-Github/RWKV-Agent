# Agent harness：工具调用、容错、收尾、长上下文

## 1. 工具目录

- **用扁平可读占位符，不用 JSON Schema**。一行一个工具，三键 `{name, description, arguments}`，参数值写成说明字符串：
  ```
  <tools>
  [{"name":"read_file","description":"Read a text file","arguments":{"path":"relative file path","start":"integer 1..200, optional"}},
  ...]
  </tools>
  ```
  模型会把 schema 对象（`{"type":["integer","null"]}`）、占位符（`"array of string"`）、示例值**逐字抄成参数值**。
- **不放示例/few-shot 块**。示范会外溢到所有问题，删掉反而涨分且请求更短。
- **保留一个"结束出口"工具**（如 `no_tool{reason}`）。7B 模型否则很难主动结束工具循环，去掉它掉分、重复调用 +30%。
  风险：重工具负载下会被当放弃口，或拿来谎报"已完成"，harness 要校验。
- 可选整数参数声明成可空并给默认值，模型会发 `null`。
- 模型**按工具名字面联想选工具，不按信息来源**：本地数据也会去调 `web_search`；不会主动用名字不直观的工具（如 `search_text`）。
  在 System 加"信息来源提示"类句子基本无效甚至有害，改工具名/描述更有用。
- 专用工具（天气等）在显式提问时会用，但任务是"写个产物"、多轮或隐式需求时会绕开。
- state 微调后的模型会背熟训练时的固定目录，去调本轮没提供的工具；目录要和训练一致，或在训练里打乱/删减目录。

## 2. 结果回传与提醒

- 工具结果放在 User 回合：`User: <tool_response>{单行 JSON}</tool_response>`（或官方 `User: Function output:\n…`）。
- 每步提醒**另起一条 User**，不要和结果合并。参考措辞：
  > Use the Tool results above to continue the current task.
  > If the evidence is sufficient, answer now. Call another tool only for a specific missing fact.
  > Never repeat a successful tool call.
- **空结果附一句中文说明，点明"再搜也没用"**（搜索次数 6.0→2.3）：
  > 没有搜到任何结果。同样的关键词再搜也不会有结果。最多换一种说法再搜一次；还是没有，就直接告诉用户没查到。不要编造。

  不要用英文 "tell the user …"（会被原样吐成终答）；不要只写"不要再搜"（会诱发编造）。
- 单个超长字符串字段：保留开头 + 与任务词最相关的窗口，总长 ~2400 字符量级。
- 多条结果（如多个子 Agent）有**强近因偏差**：模型偏信最后一条。合并成一条并带来源标签比分开回喂好；"请比对来源"类提示无效。

## 3. 解析容错（收益最大的一层）

按优先级接受这些"不规范但意图清楚"的输出：

- **recover-preamble**：先写一句"我先查一下……"，换行，再一个完整调用。G1 系列很爱这样写，严格解析会判成终答。
  接受后 G1L 通过题 +42%，是单项最大收益。限制：调用另起一行、前文不含 ```` ``` ````、只有一个调用、生成没撞顶。
- 剥掉思考块（包括没闭合 `</think>` 就开始写调用的情况）。
- **OpenAI 外壳**：`<tool_call>` 里写 `{"type":"function","function":{"name":…,"arguments":…}}` → 拆成 `{"name","arguments"}`。G1L **开思考后**很爱这样写（不开思考少见），严格解析器报 `unknown field "type"`；"先说话 + 外壳"要和 recover-preamble 共用同一套拆壳逻辑，否则兜底救不回来。
- **完整对象后多出 `}`**（`…}}}`）：去掉多余右括号再解析。G1L 思考模式下与外壳同样高频。
- 裸 JSON 或另一种信封（```` ```json ````、`<tool_call>` 互换）。
- `arguments` 是字符串化 JSON → 再解析一次。
- 键名别名：`cmd/tool/args/parameters` → `name/arguments`；参数被提到顶层 → 收回 arguments；嵌套 name；缺 name 时按参数推断。
- 小的 JSON 语法修复（尾逗号、缺括号）。
- **标量宽松**：数字字段接受 `"10"`，布尔接受 `"true"`；数字带千分位 `"6,412"` 要归一化。否则一次拒绝 + 重复拦截会耗光步数。结构性错误仍严格报错。
- 模型会编造绝对路径（训练残留，如 `/home/xxx/workspace/...`），映射到工作区相对路径（取最后一个 `workspace/` 之后）。

## 4. 重复调用与收尾（头号死因）

RWKV **会照抄自己上一回合**：刚输出过某个调用，下一步很容易原样再来一次（首次重复中过半紧邻上一步）。
提示词、提醒位置、采样都只能压低约 20%，根治要靠训练数据里"读到即答"的示范。harness 侧：

1. 同一精确调用只执行一次；同一工具连续失败两次后拒绝第三次。
2. 拒绝提示逐级加强：首次 `This exact call is disabled. Do not repeat it.`；连续 3 次以上带剩余步数 `STOP repeating …`。
3. **重试时不要把被拒的调用回显进上下文**（RWKV 会照抄）。
4. 到阈值关闭全部工具、强制收尾，收尾提示作为独立 User 块：
   > That tool call was rejected because it repeats an earlier failed call.
   > Tools are now unavailable. Answer from the Tool results, and clearly state anything that could not be verified.
5. **作答阶段还在吐工具调用**是另一大死因（"tools are now unavailable" 常被无视）。兜底：重试用完后预填 `根据上面的工具结果，` 再生成一次。

## 5. 长上下文与网页

7B 量级的经验：

- **总结**任务约 12K token 内健康，16K 以上崩；**问事实**时 ≤3K 几乎全对，3–6K 约一半，6K 以后 2–4 成，后半页基本丢。
  → 网页按 **6K 真实 token** 截断，先去掉 Markdown 链接 URL 和图片（维基页能减半），附说明"只给出了前面一部分，重复抓取同一网址也拿不到更多内容"。
- 英文长网页（≥6K）会让终答漂成英文。
- **RWKV 7B 自摘要会编造**日期、数字、网址，让它挑段落也挑不对。替代：确定性截断/抽取；或用外部模型摘要；
  或摘要后把原文里不存在的数字/日期/版本号所在句整句删掉。
- 整页喂回时模型不在页内找答案，而是再去抓取；压缩后反而能答。
- 压缩/抽取指令按页面语言切换：英文页用逐句摘抄；**中文页用摘抄会逐字复读**，改用"最多 3 句、只用原文词句、不提任务、无开场白"。
- **读了就忘**：早先读到的内容在后续步骤功能性失效，甚至自信否认存在。往 transcript 里引导一次检索命中最有效；给读取结果加行号无收益。

## 6. 终答

- 终答常违反格式契约（加解释句、路径前缀、加粗），但内容是对的 → 判分/解析要宽容，或训练纠正。
- 查不到时不要裸回 `UNKNOWN`，应写清查了哪、缺什么、下一步。
- 子任务结果不要逐条回显成大段，模型会被最近一条带偏。
