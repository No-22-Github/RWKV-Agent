---
name: rwkv-tricks
description: 驱动 RWKV-7 G1 系列模型（7B/13B，rwkv_lightning 推理后端）的通用技巧与模型癖好——prompt 字节格式、Assistant: 生成点、预填/锚点、think 写法、采样与复读惩罚、停止符、复读检测、工具调用格式与解析容错、长网页截断、state/MiSS 训练数据渲染、rwkv_lightning 接口怪癖。凡是在任何项目里给 RWKV 拼 prompt、写 Agent harness、调采样参数、解析 RWKV 输出、渲染 RWKV 训练语料、对接 rwkv_lightning 接口时都要用；用户说"RWKV 老是复读""英文题答成中文""工具调用格式乱""arguments 是字符串""不停输出 User:""加个预填/锚点""调一下采样"时一定要用。正式跑分用 rwkv-bench。
---

# rwkv-tricks：驱动 RWKV 的通用经验

来源：RWKV-Agent 仓库 2026-08～10 的实测（G1i/G1j/G1k/G1L，7B 为主，13B 部分验证）。
数字只用来说明量级，具体分数会随 checkpoint 变；**规则本身是跟模型和分词器走的**。
换了新一代模型，先用小探针复核"随模型变化"标记的条目。

RWKV 对 prompt **字节**极其敏感：多一个空格、少一个空行、大小写不对，接口不报错，输出静默变差。
**检查真正发出去的字节，不要检查脑子里的模板。** 调试第一步永远是把最终 prompt 原样打印出来。

## 十条铁律（先过一遍）

1. **生成点以 `Assistant:` 结尾，冒号后不留空格。** 多一个空格：英文题大面积改用中文作答、自己续写下一轮 `User:`。中文题看不出来，所以容易漏。→ [prompt-format.md](references/prompt-format.md) §1–2
2. **块结构**：`System: …\n\nUser: …\n\nAssistant:`。块间恰好一个 `\n\n`，块内不能有空行（先清洗 System/User 文本），标签大小写和半角冒号都要对，`System:` 只放一个、放最前。
3. **预填（种子）的最后一个 token 必须是训练里独立出现过的 token。** `<think>`、`<tool_call>` 这种 `>` 结尾的不安全，要扣掉 `>` 让模型自己补：`<think`、`<think></think`。
4. **思考用 `Assistant: <think`（完整）或 `Assistant: <think></think`（假思考）。** 开思考就给足 token 预算（≥1024，最好 2048–4096），否则测到的是截断。thinking=off 时模型也会自发写 `<think>`，解析器必须能剥。
5. **采样**：Agent 用 `T=0.3, top_p=0.5, top_k 不截断, presence 0.5, frequency 0.1, decay 0.996`。截断（top_p）比温度重要；`top_k=1` 时温度失效；presence ≥1.0 会掉分；T=1（官方 demo 参数）最差。→ [sampling-stop-loop.md](references/sampling-stop-loop.md)
6. **停止条件同时给 EOS(0) 和 `User`(24281)**，或文本停止串 `\n\nUser:`。基模调完工具经常不发 EOS，会自己编下一轮。
7. **客户端做复读检测**：最近 768 字符里 24 字窗口的"新鲜率" <5% 就截断。惩罚参数压不住整段循环。
8. **工具调用会照抄上一回合**，这是 Agent 头号死因。harness 要拦截重复调用、不要把被拒的调用回显进上下文、到阈值强制收尾。→ [agent-tools.md](references/agent-tools.md)
9. **工具目录用扁平可读占位符，不用 JSON Schema，不放示例块。** 模型会把 schema 对象、示例值逐字抄进参数。保留一个 `no_tool` 之类的"结束出口"。
10. **解析器要宽容**：接受"一句说明 + 换行 + 一个完整调用"、字符串化的 arguments、数字写成字符串 `"10"`、`true` 写成 `"true"`。宽容解析比改提示词收益大得多。

## 参考文件（按需读）

| 文件 | 什么时候读 |
| --- | --- |
| [prompt-format.md](references/prompt-format.md) | 拼 prompt、写预填、开思考、看分词切法 |
| [sampling-stop-loop.md](references/sampling-stop-loop.md) | 调采样、设停止符、处理复读/不停输出 |
| [agent-tools.md](references/agent-tools.md) | 写 Agent harness：工具目录、结果回传、解析容错、重复拦截、收尾、网页与长上下文 |
| [rwkv-lightning-api.md](references/rwkv-lightning-api.md) | 对接 rwkv_lightning HTTP 接口、并发、state/adapter 上传 |
| [training-data.md](references/training-data.md) | 给 state tuning / MiSS / LoRA 渲染训练语料、挑数据 |

## 调试顺序（输出不对时）

1. 打印最终 prompt 的原始字节（`repr`），对照铁律 1–3 检查空格、空行、大小写、预填结尾。
2. 用词表做一次贪心分词，看生成点前最后几个 token 是否和训练分布一致。
3. 看原始输出（不是解析后的）：是不是先写了一句话再调用、是不是自发写了 `<think>`、是不是续写了 `User:`、是不是在复读。
4. 再看采样参数：是否 `top_k=1` 却以为有温度、是否吃了后端默认重惩罚。
5. 最后才改提示词措辞——而且改完先看**行为分布**（直接作答 / 调工具 / 弃权各占多少），再看总分。精简提示和详细提示总分可能接近，但做对的是两批不同的题。

## 一些反直觉的经验

- **约束 RWKV 的是字节形状，不是自然语言指令。** "Return only JSON" 不如直接预填 `{"name":"`。
- **示例块是负资产**：few-shot 示范会外溢到所有问题，删掉反而涨分、请求还变短。
- **违反率 ≠ 价值**：某条规则模型 20/20 都违反，删掉它照样可能让某些题翻挂。删提示词句子要 A/B。
- **提示语言会带偏输出语言**：系统提示里的中文会拖英文题，英文长网页会让终答漂成英文。
- **工具倾向是二态的**：一个 checkpoint 要么很爱调工具、要么很少调，中间态少；"弃权分高"常常是畸形调用被判成弃权白送的。
- **思考失控也是二态的**：要么几百字符收敛，要么写到上限，没有中间态。
- **贪心也不完全确定**：批推理下同一题会有 ±1–3 题的抖动，A/B 必须同一时间窗成对跑。
