# DeepSeek-flash 作为蒸馏老师 — 筛选报告

日期：2026-10-10。HEAD `2d29766`，`local/bin/rwkv-cli-chat`（`go build -tags chatcompletions`，同一 HEAD，工作区干净）。
对照：同日 [MiniMax-M3.1-Flash 筛选](../minimax-teacher-20261010/REPORT.md)，套件、步数、预算一致。

## 结论

1. **两套都比 MiniMax 高**：workbank 严格 **143/148**（MiniMax 132/148），bfcl-product **60/60**（MiniMax 53/60）。
   配对逐题：workbank DeepSeek 独过 11、MiniMax 独过 3（双侧符号检验 p≈0.057）；bfcl DeepSeek 独过 7、MiniMax 独过 0（p≈0.016）。
   bfcl 差距全在多轮：recovery 10/10 对 5/10，state 10/10 对 9/10。
2. **思考比 MiniMax 更频繁、更短**：workbank 69% 的步有思考（MiniMax 44%），中位 154 字符（MiniMax 297），p90 1128；全是英文。
3. **快且不限流**：8 并发下 workbank 148 题 5.7 分钟，没有 429；bfcl 两段合计约 1 分钟。
4. **一个接口限制**：思考模式下不接受 `tool_choice: "required"`（HTTP 400）。workbank 不发这个值，不受影响；bfcl 的工具调用题会发。

## 设置

| 项 | 值 |
| --- | --- |
| 端点 | next-token.cc 中转，模型 `deepseek-flash`（OpenAI 兼容，原生工具调用） |
| 思考 | `--chat-thinking auto`：端点默认返回 `reasoning_content`，逐步记进 trace |
| 采样 | `--temperature 0.3 --top-p 1`（T=0 会崩，见 [dsflash 摸底](../../workbank/reports/dsflash-baseline-2026-09-22.md) §2；MiniMax 用的是官方推荐 1.0 / 0.95） |
| 预算 | 16 步、4096 / 4096 token、单题 30 分钟、**8 并发**（两套同时跑，合计 16） |
| workbank | `--cases bench/workbank/cases --include-draft --tool-catalog work-v1 --file-tools lines` |
| bfcl-product | `--suite bfcl-product --agent-protocol xml` |

闸门：`run check --arm t03-p10` 只有一项不过：`decision_max_output_tokens` 为 4096，而闸门要求 2048。
2048 是 RWKV 的规定；这里沿用 MiniMax 筛选的 4096，因为带思考的 API 模型在 2048 下容易被截断。其余各项都通过。

## 作废与重跑

| run | 作废 | 处理 |
| --- | --- | --- |
| workbank | log-0012：HTTP 500（传输错误） | 同配置单题重跑，通过，合并 |
| workbank | code-0004：工具参数不是合法 JSON（`"path": .`） | 模型输出缺陷，计失败 |
| bfcl-product | 30 道带工具调用的题（supplied 10、state 10、recovery 10）：思考模式拒收 `tool_choice: "required"` | 这 30 题用 `--chat-thinking disabled` 重跑，30/30，合并。所以 bfcl 这 30 题的分数是**不开思考**测出来的 |

## workbank 失败（3 道，外加 1 道作废计失败）

| 题 | 现象 | MiniMax |
| --- | --- | --- |
| log-0017 | 找 FATAL 条目的模块，答 UNKNOWN | 过 |
| web-0008 | 查某参数在哪个版本废弃，答 UNKNOWN | 过 |
| scr-0016 | 修 `tally.py`：16 步用完还没写文件，终答把整份代码贴出来 | 过 |
| code-0004 | 工具参数 JSON 非法（见上） | 过 |

3 道都是能力或收尾问题，不是判分口径问题。

## 用作老师时要注意

- **工具选择**：蒸馏走 workbank 同款 harness，不发 `tool_choice: "required"`，可以开思考。以后某套件要强制调工具，就得关思考，或者 harness 改发 `auto`。
- **思考形状**：步级思考占比 69%，比 g1k 和 MiniMax 都高；短步思考很短（中位 154 字符）。带思考版训练行的分布会和 MiniMax 版不同，选老师时要一起考虑。
- **非法参数**：148 题出现 1 次 JSON 非法的参数，collect / render 阶段会被拒收，不会进训练数据。
- **温度**：只能用 T>0，沿用 0.3。

## 产物

`local/runs/bench-20261010-deepseek/`（不入库）：`dsf-workbank-k0`（主 run）+ `dsf-workbank-k0-rerun`（log-0012），
`dsf-bfclp-k0`（30 题有效）+ `dsf-bfclp-k0-nothink30`（关思考重跑 30 题），`run.sh` 为运行脚本。
