# G1L 提示词 / 工具格式消融（2026-10-24）

## 要回答的问题

G1L 预览版（`rwkv-g1l-7b-temp-3797`，无 State / MiSS）在 Agent 场景下，哪种提示词和工具格式最好？
结论用来写 RWKV prompt 经验文档（`docs/guides/rwkv-prompt-guide.md`），并决定是否改 `agent-wire-v1.0` 的默认值。
改默认值后重跑分、重渲染训练数据都可以接受。

## 口径

- 考卷 `bench/exam/full.json`（agent-exam-v1.2，568 题，`--harness app`），scorer-v4，harness v23。
- 端点 8018 网关直连（`http://100.64.0.4:8018/v1`，3 卡，albatross-1.3.0），前后各拍一次 models / server/status。
- 采样 `agent-fast`，`--api-stop-tokens 0,24281`，与 10-20 G1L 基模那次一致。
- 每组 k0 + k1 两遍，两遍并行各 32 并发（总 64）。
- 二进制从干净的 main 构建（commit 写进 run.json）。

## 组别（第一轮）

| 组 | profile | 测什么 |
| --- | --- | --- |
| `base` | `agent-wire-v1.0`（`--strict-spec`） | 当前默认 |
| `rp` | `agent-wire-v1.0+recover-preamble` | 参照组：接受"一句说明 + 调用"（10-20 已知 +8 点） |
| `sp` | `rp+gen-space` | 反例：生成点 `Assistant:` 后多一个空格 |
| `tf` | `rp+think-fast` | 官方"假思考" `Assistant: <think></think` |
| `tF` | `agent-wire-think-v1.0+recover-preamble` | 完整思考 `Assistant: <think` |
| `mu` | `rp+merge-users` | 连续 User 合并（结果 + 提醒放同一条），贴近官方严格轮替 |
| `md` | `md-fence-v1+prefill-none` | 官方函数调用写法：`System: Tools:`、```` ```json ```` 围栏、`User: Function output:` |
| `nn` | `rp+merge-users-no-nudge` | 去掉每步提醒，工具结果直接挨着生成点（补充组，见下） |
| `lead` | `rp+merge-users-lead` | 提醒、被拒说明、收尾指令都挪到结果前面，结果永远在最后（补充组） |

补充组的来由：`rp` 里 53% 的题出现过"重复上一次成功调用 → 被拒 → 强制收尾"，这些题通过率 20%（其余 43%）。
每步工具结果后面跟着约 53 token 的 `User:` 提醒，把证据从生成点推远；RWKV 是 RNN，离生成点越近的内容越"新鲜"。
`nn` 测"不提醒"，`lead` 测"提醒还在、但证据在最后"，两者对照能区分是提醒的位置问题还是提醒本身多余。
补充组用 564c2573 构建的二进制（只新增 lead 取值，其它预设 hash 不变），第一轮其余组用 9cfbb65e。

## 主指标与判定

- 主指标：两遍 strict 通过题数均值（作废计失败）。
- 每组对 `rp` 做逐题配对：翻转 +a/−b、符号检验 p。
- 差距小于 `rp` 两遍之间的差 → 写"无法区分"。p < 0.05 且两遍同向才算有效。
- 第二轮（采样）在第一轮最好的组上做；第三轮（提示词措辞、结果回传写法）在前两轮最好的组合上做。

## 第二轮：采样

第一轮全部用 `agent-fast`（带 presence/frequency 惩罚）。G1L 和新考卷上都没扫过采样（上次是 09-23 的 G1K + workbank）。
固定第一轮胜出的格式，只换采样，每档 k0 + k1：

| 档 | 参数 | 测什么 |
| --- | --- | --- |
| `agent-fast` | T0.3 top_p0.5 presence0.5 freq0.1 decay0.996 | 第一轮已跑，直接复用 |
| `agent-default` | T0.3 top_p0.5，无惩罚 | 只去掉惩罚 |
| `greedy` | top_k1 | 确定性下限 |
| `agent-stable` | T1 top_k20 top_p0.3，无惩罚 | 高温 + 强截断 |
| `official` | T1 top_p0.5 presence1.0 count0.1 decay0.99 | 官方 Gradio demo 默认值 |
| `pr10` | T0.3 top_p0.5 presence1.0 freq0.1 decay0.996 | 惩罚加重 |

关注点：惩罚会压 JSON 里反复出现的 `"` `:` `{`，看工具调用 JSON 损坏率和重复调用率是否随惩罚变化。
