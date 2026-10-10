# MiniMax-M3.1-Flash-Preview 作为蒸馏老师 — 筛选报告

日期：2026-10-10。HEAD `adf9d94` 起的 `rwkv-cli`（`-tags chatcompletions`）。M3 因价格与速度被用户排除，只测 Flash。

## 结论

1. **能力足够当老师**：workbank 148 严格 132（89%），去掉 7 道 Token Plan 限流（429）题为 132/141（94%）；
   bfcl-product 53/60（irrelevance 20/20，中文 33/40）。对照：g1k 基模开思考 workbank 约 11/148。
2. **失分几乎都是答案形式**：workbank 9 道真失败里只有 1 道算错（log-0005：26 vs 27），其余是 `US$` 前缀、答案裹解释句、该追问时直答、脚本题等；
   bfcl 7 道里 5 道是 recovery 多轮的第一轮写「没有找到」而判据要「不存在」（第二轮答对了值）。
3. **思考风格贴近 g1k**：44% 的步有思考（简单步不想），中位约 300 字符、p90 约 1300，全部英文电报式（中文题也用英文想）；
   与 g1k think-full 的中位 200–340 字符同量级（见 [think-shape.md](../think-full-20261010/think-shape.md)）。
4. **速度**：3 并发下 workbank 148 题 13.6 分钟、bfcl 60 题 3 分钟。Token Plan 并发上限低，48 并发几乎全 429，放量时按 2–3 并发排队。

## 设置

| 项 | 值 |
|---|---|
| 端点 | `https://api.minimax.cn/v1/chat/completions`（OpenAI 兼容，native-chat，原生工具调用） |
| 思考 | `--chat-thinking split`（发 `reasoning_split:true`，思考进 `reasoning_content`，Step 记录为 `reasoning_content`） |
| 采样 | `--temperature 1.0 --top-p 0.95`（官方推荐） |
| 预算 | 16 步、4096 / 4096 token、单题 30 分钟、3 并发 |
| workbank | `--cases bench/workbank/cases --tool-catalog work-v1 --file-tools lines --include-draft` |
| bfcl-product | `--suite bfcl-product --agent-protocol xml`（默认 markdown 协议带 semantic no_tool，与原生工具调用不兼容） |

bfcl 的协议（xml + 原生工具）与 RWKV 的 g1k 文本协议不同，分数只作能力参考，不与 RWKV 直接比。

## 接口对比（同一上下文，各 3 次）

官方推荐 Anthropic 接口（支持交错思考，thinking 块需原样回传）。在 log-0001 的三个上下文上各发 3 次：两种接口的思考频率与长度无实质差别，
简单步（读完目录后决定读哪个文件）两边都 0/3 思考，计数步两边都写 30–270 token 的计数过程。harness 继续用 OpenAI 接口，`reasoning_content` 会回传。

## 用作老师时要处理的

- 终答形式：bfcl/中文场景爱写 Markdown 长回答（表格、加粗）；渲染训练行前按 think-shape.md 的规格只保留题目要的值，或在老师附加指令里要求裸值。
- 思考语言：中文题也用英文思考，与 g1k 一致，不用改。
- 并行调用：偶尔一次发两个工具调用，harness 只取第一个（parallel_tool_calls=false）。
- 限流：429 会让题目作废，放量脚本要串行、低并发，并对 429 题重跑。

## 产物

`local/runs/bench-20261010-minimax/m31f-{workbank,bfclp}-k0`（不入库）；首次 48 并发被限流的 run 在 `aborted-429/`。
