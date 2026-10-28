# 采样、停止符与复读

## 1. 采样参数

rwkv_lightning 的六个字段：`temperature` `top_k` `top_p` `alpha_presence` `alpha_frequency` `alpha_decay`（均生效）。
OpenAI 兼容的 chat 接口一般只发 temperature/top_p/presence/frequency，**top_k 和 decay 发不过去**。

| 预设 | T | top_k | top_p | presence | frequency | decay | 用途 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| agent-fast（推荐） | 0.3 | 不截断（65536） | 0.5 | 0.5 | 0.1 | 0.996 | 多步 Agent；轻惩罚压复读、更快 |
| agent-default | 0.3 | 不截断 | 0.5 | 0 | 0 | 1 | 单步工具决策 |
| stable | 1 | 20 | 0.3 | 0 | 0 | 1 | 少量重复的 A/B，跑间方差最小 |
| greedy | 1 | 1 | 1 | 0 | 0 | 1 | 回归调试 |
| 后端默认 | 1 | 20 | 0.3 | 2 | 0.2 | 0.996 | 只适合闲聊，输出长度减半 |

经验：

- **截断比温度重要**。有 top_p 截断时 T 怎么变分数都稳；不截断时 T 从 0.3 升到 1.0 掉一半。
- **`top_k=1` 时温度失效**，实际就是贪心。很多"T=0.3"的历史结果其实是贪心。
- **想要真贪心必须显式写全**：`top_k=1, top_p=1`，并把 presence/frequency 归零、decay=1。否则会吃到后端默认的重惩罚。
- **轻度惩罚不会写坏 JSON**（损坏率反而比无惩罚低）；presence 加到 1.0 就开始掉分。
- **T=1 是最差的维度**，官方 Gradio demo 参数（T1 p0.5 presence1.0 count0.1 decay0.99）不适合 Agent。
- 副作用：agent-fast 这类低温档让模型更倾向直接调用，需要追问用户时变差。
- **贪心也不完全确定**：批推理下会有小抖动，A/B 要同时间窗成对跑，按题配对比较。

## 2. 停止符

- 基模经常**不发 EOS(0)**，而是直接续写下一轮 `\n\nUser:`（`\n\nUser:` 切成 261 / 24281 / 59）。
- 停止条件同时给：整数 `[0, 24281]`，或文本停止串 `\n\nUser:`。实测批推理耗时降一个量级。代价：24281 是裸 `User`，正文/代码里出现 `User(...)` 也会被截断（bsh-0150 因此思考块不闭合）；带思考或会输出代码时只给 `[0]` 并在客户端按 `\nUser:` 截断。
- 只停 `\nUser:` 会漏掉 `✿User:` 之类变体。
- 裸续写时模型有 `✿` 文档边界习惯（`✿text1✿`、`i✿reverse_word`），必要时把 `✿` 也加进停止集。
- 客户端常用文本停止串：调用信封 `</tool_call>`；`\nUser:`、`\nSystem:`；md 围栏格式还可加 ```` ``` ````、`</s>`。
- **不要把 `\n` 类 token 放进服务端停止列表**，会把多行工具参数截断。
- 停止串和参数内容可能冲突（参数里含 ```` ``` ````），信封格式选型时要考虑。

## 3. 复读与循环

RWKV 的复读形态：整段重复一句话/一段命令；JSON 标点塌缩成 `":"":"`；终答答完继续逐字复读。
**采样惩罚压不住整段循环**，需要客户端检测并截断。

### 流式 loop-guard（已在 7000+ 条输出上校准，0 误报）

最近 768 个字符中，以 24 字符滑窗计，"在本次输出里首次出现"的窗口占比 < 5% → 判为循环，立即截断并按 length 结束。
撞上限的生成里能抓到约 88%、省约 3/4 token；漏网的是"行号递增的逐行抄日志"这种近似重复。

```python
class LoopGuard:
    GRAM, WINDOW, FRESH_MIN = 24, 768, 0.05

    def __init__(self):
        self.text, self.seen, self.fresh, self.tripped = "", set(), [], False

    def write(self, chunk: str) -> bool:
        if self.tripped:
            return True
        for ch in chunk:
            self.text += ch
            if len(self.text) < self.GRAM:
                continue
            gram = self.text[-self.GRAM:]
            is_new = gram not in self.seen
            self.seen.add(gram)
            self.fresh.append(is_new)
            if len(self.fresh) > self.WINDOW:
                self.fresh.pop(0)
            if len(self.fresh) == self.WINDOW and sum(self.fresh) < self.WINDOW * self.FRESH_MIN:
                self.tripped = True
                return True
        return False
```

### 非流式摘要/压缩输出的退化检测

满足任一即判复读并回退到原文：≥6 行且唯一行占比 < 0.6；连续 ≥4 行相同；12-gram 唯一率 < 0.35。

### 撞顶判定

rwkv_lightning 跑满 max_tokens 时 finish_reason 可能仍报 `stop`，有的部署只发 `[DONE]`。
用"生成 token 数 ≥ 请求上限的 98%"判定撞顶，别信 finish_reason。
