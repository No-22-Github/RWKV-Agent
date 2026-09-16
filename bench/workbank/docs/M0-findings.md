# M0 核实结论（workbank 前置，2026-09-17）

> 调研方式：上游源码 clone（/tmp/rwkv_lightning_cuda-src）+ 仓内代码核对 + 本地端点轻量探测。
> 三个调研子 Agent 的完整证据（file:line）在各自报告中；本文只留结论与决策。

## 1. `data_query` 数字解析 —— **不自动清洗，埋法维持但机制改写**

- data_query 是 filter+aggregate 形态（非 SQL）。单元格解析只做 TrimSpace + ParseFloat：`"$1,234.50"`、`"12.5%"`、`(300.00)`、`NA`/`-`/`null`/空串**全部保持字符串**（`internal/agent/tools/assistant.go:1189-1217`）。
- 聚合（sum/avg/min/max）遇非数值单元格**整个调用报错**（`field %q is not numeric`，assistant.go:1064-1065），不跳过、不容忍。
- filter 比较是「数值优先，否则大小写不敏感字符串相等」（assistant.go:944-951）。
- **决策**：TR-NUMFMT / TR-MISSING 埋法不变（题面禁词不变），但 authoring 起草提示要写明真实机制——陷阱的代价是「data_query 直接聚合会报错或得不出数」，模型必须改走 read_file+calculator 或先清洗。NOTES 里错误答案的写法照旧。
- 注意：boundary 套件不注册 data_query；work-v1 目录将注册（见 §6）。

## 2. 观测工具行为（TR-TRUNC / TR-LONG 的精确参数）

| 项 | 实际行为 | 对出题的意义 |
|---|---|---|
| `read_file` 截断 | 64KB（`tools.go:22`），模型可见 `truncated: true` JSON 字段，无文本标记 | TR-TRUNC 的 >64KB 文件成立；截断信息只有 JSON 字段 |
| `read_lines` | 窗口 ≤200 行/次；底层同样 64KB 上限且**静默丢弃**、无 truncated 标志（`fileedit.go:34-35`） | 长 CSV 靠 read_lines 读完是陷阱盲区，TR-TRUNC 题优先让 read_file 触发 |
| `list_files` | 默认 max_results=200（schema 上限 500），`truncated` 恒在输出里；**dotfile 会列出**（只跳 .git/build/dist/node_modules） | 「文件数 >500」的 TR-TRUNC 仍成立；隐藏文件在场是 TR-DECOY 可用素材 |
| fetch 压缩阈值 | **常量 4096 真实 token/页**（`runner_compression.go:45`），另有 8192 token/调用 的多页共享硬截断（`web.go:41`）；默认开，但依赖进程内词表 | TR-LONG 的 web 页按 >4096 token 设计；计划案里 4673–5021 的旧区间作废 |

## 3. seed（H4 结论）—— **后端不支持，不改后端，manifest 如实记录**

- CUDA 服务端 HTTP 层不解析 `seed`（`parse_options` 无此字段），采样种子每次生成随机产生（`rwkv_sampler.cpp:14-19`）；传入被静默忽略（实测 200）。
- 贪心解码等价物：`temperature=0.001, top_p=0`（temperature=0 会 400）。
- 决策：harness 加 `--seed` flag 仅做两件事——写入 manifest `sampling.seed`、chat-completions 通道透传（SDK 已支持）；rwkv-lightning 路径不发送（发了也没用）。workbank 跑分按计划用 temperature 0.3，接受服务端随机播种，**可比性靠 k=4 与极差闸门，不靠 seed**。结论写进 manifest 的 H4 备注由 ledger.py 落账。

## 4. `/big_batch/completions` —— **CUDA 后端不存在，不启用**

- 该接口属于 Python 后端（rwkv_lightning_api_doc.md 前半部）；CUDA C++ 服务源码零命中，实测 404。
- CUDA 等价物是 `/v1/batch/completions`（`contents: string[]`，服务端按 token 长度重排、锁步解码、按 index 对齐返回），**harness 现行路径已经就是它**（G1K 消融记录：`--api-url http://100.64.0.1:18222/v1/batch/completions`，client 每次发单元素 contents）。
- 并发模型：服务端有 VRAM 自适应准入 + FIFO 队列（无排队上限），`hard_max_bsz` 当前 1423，`concurrent_generation` 能力在。**决策：不加客户端改动**，case-parallelism 并发单元素请求即可，服务端自行合批。
- 附带坑（记账用）：batch 响应无 usage、`finish_reason` 恒 `stop`（截断不可辨）——harness 已按本地 token 计数处理，ledger 不依赖服务端 usage。

## 5. 现行 wire profile（G1K 最终配置）

- `--profile xml-v1+align-qwen36+no-tool+bare+one-stage`（ad-hoc 组合，非注册 preset）
- canonical: `format=xml;transcript=product;transport=text;thinking=off;prefill=none;abstain=no-tool;terminal=none;route=none;catalog=full;control=bare;feedback=raw;subagent=block;align=qwen36;stages=one;loop=0,...,false`
- wire_hash `51859aff55ce8e7da6f318d3403db163675b57778b5e79d192e661a456422457`（与 runs/ablation-g1k/r4-one-stage/run.json 逐字节一致）
- **manifest 缺口**：`--profile` 修饰串不落盘（只有 canonical/hash），ad-hoc 时 `wire_preset` 为空 → M1 补记 `wire_profile` 原串。

## 6. M1 实施清单（由缺口反推，全部并入计划案 H1–H4）

1. schema v5：`tags` 透传对象；case 级 `web_fixture`（`WebFixtureEntry` 补 `published_at`，Brave 真路径已有 age→published_at 先例）；`expect.files`（equals/contains/absent/unchanged）；`expect.run`（python3 -I -S、10s、stdout 逐行、hidden_files）；`expect.max_calls`（按模型发出计，含 duplicate 被拒）；放宽 `caseio.go:142-151` 的「每轮必须声明工具期望」——有 expected_number/output_*/files/run 任一即可。v4 照常加载。
2. `--cases` 目录模式：递归找 `case.json`（现有目录路径被 primitive trusted-dir 占用，以「目录内发现 case.json」区分走 workbank 加载）；`--include-draft` 控制 `tags.status == "draft"` 是否载入。
3. `--tool-catalog work-v1`：§2.4 十二工具 + 固定时钟 `2026-09-16T10:00:00+08:00` + web 工具恒注册（fixture 空→空结果/固定 not-found 页）；manifest 记 `tool_catalog_hash`。
4. 题级干预计数：从每题内嵌 agent.Result 的 step 流聚合 `rescues / forced_answers / duplicate_rejects / protocol_repairs` 到 CaseResult 新字段（数据已在，只缺聚合与落点）。
5. manifest 补账本字段：`wire_profile`（原串）、`state_id`/`state_sha256`、`tool_catalog_hash`；model fingerprint 远程路径本来为空，ledger 以 `model_id + endpoint` 代之（不改 harness）。
6. `trap_hit` / `redundancy` / `ref_calls` 比对：不在 harness 做，由 M2 `ledger.py` 读 tags + summary.json 计算（harness 不该知道题库语义）。
7. H4：`--seed` flag → manifest + chat 通道透传（见 §3）。

## 7. DeepSeek 通道（chat-completions）接线要点

- 构建须带 `-tags chatcompletions`；`--chat-token-limit-field max-tokens`（DeepSeek 不认 max_completion_tokens）。
- `--chat-prompt-mode native-chat`（默认）+ `--thinking off`（native-chat 强制）；工具目录以 OpenAI function schemas 发送。
- 顶层非标 `{"thinking":...}` 字段是否被 next-token.cc 拒绝待冒烟实测；`thinking=disabled` 时不发该字段则无此风险。
- usage 含 reasoning_tokens 分离；`reasoning_content` 已按 extra field 读取——与 DeepSeek 响应格式吻合（实测通过）。

## 8. 对出题手册的三点修订（起草提示里生效）

1. TR-NUMFMT/TR-MISSING 的「不注意会得到的错误答案」改为描述 data_query 报错/空结果后的典型手算错误，而不是「工具自动清洗导致错值」（工具不会清洗）。
2. TR-TRUNC 埋 read_file 64KB 截断（truncated 标志可见）；不要指望 read_lines 读长文件（静默 64KB 截断是双刃， lint 会按场景提示）。
3. web 题页面 token 量按 4096（压缩线）/ 8192（硬截断）两档设计。

## 9. 新发现：工作区工具不创建目录（出题约束 + lint 规则）

`workspace.resolve`（internal/agent/tools.go:175-193）对相对路径做 `filepath.EvalSymlinks`，
**中间目录不存在直接 ENOENT**，`write_file` 的 MkdirAll 永远走不到——模型无法向
不存在的子目录写文件（无 mkdir 工具）。这是交互 agent 的既有行为，不在 H1 四项
范围内、不改；对题库的处理：

- **出题规则**：凡要求写入 `dir/xxx` 的题，`files` 必须预置该目录的占位文件（如 `dir/.keep`）。
- M2 的 lint.py 落一条机器检查：`expect.files` / 题面引用的写入目标目录必须在 `files` 中存在。
- 附带语义：这也是合法的 ERR 轴素材（模型遇到写失败应换路径或报告），但**不得**作为
  未声明的陷阱——要么预置目录，要么在 NOTES/tag 里如实声明。
