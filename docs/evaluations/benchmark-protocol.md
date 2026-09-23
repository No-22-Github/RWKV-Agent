# 跑分规程（Benchmark Protocol）

适用于本仓库所有正式跑分：RWKV 自家模型与作为参照的 API 模型（Qwen、DeepSeek 等）。
目标只有一个——**让两次跑分的差异只来自被测对象**，而不是格式、采样、二进制、题库版本或端点漂移。

执行时用 skill `.claude/skills/rwkv-bench/SKILL.md`（检查单）；本文是依据与细则。
本规程里的每一条都对应一次真实踩过的坑，出处见 §9。

---

## 1. 格式口径（锁定）

| 被测对象 | 传输 | 格式 | 必带参数 |
|---|---|---|---|
| RWKV（rwkv_lightning 系后端） | 续写 | **`g1k`** | `--profile g1k --strict-spec` |
| API 模型（Qwen、DeepSeek…） | 原生 Chat Completions | 推理端自己的对话模板与 `tools`/`tool_calls` | `--completion chat-completions`（不传 `--profile`） |

- `g1k` 是 `xml-v1+align-qwen36+no-tool+bare+one-stage` 的注册短名，两种写法 canonical 与 hash 完全相同
  （`TestG1KPresetIsTheLockedLonghand` 守护）。它是 2026-09-15 消融选定的格式，也是 700 条训练语料主轨道的渲染格式。
  逐字节契约见 [`docs/corpus-g1k-wire-format.md`](../corpus-g1k-wire-format.md)。
- **不传 `--profile` 不会报错，而是静默落到 legacy 默认格式**（md-fence / 两阶段 / 带示例块）。
  2026-09-22 的 g1k 148 题就这样跑出 0/148、作废 30。`--strict-spec` 只拒绝未注册组合，挡不住"忘传"——
  所以跑后必须核对 `run.json` 的 `harness.wire_preset == "g1k"`（§6）。
- API 模型的对话模板由推理端负责，不是我们的事。注意：chat 路径下 `run.json` 的 `wire_canonical` 仍会写一串
  md-fence/legacy，**那是记录缺陷，实际未生效**；判断走的是哪条路径看 `model.completion`。
- 两个例外，保留各自的协议：
  - `primitive-orig30` / `primitive-feedback30`：套件自带 benchmark transcript（md-fence + `submit`）。
  - 官方 BFCL（`scripts/bfcl.sh`）：自有 MD 锚点 / XML 裸 / XML 锚点三档，不与 workbank 混比。

## 2. 二进制与环境

- **只用从当前 HEAD 编译的二进制**：`go build -o bin/rwkv-cli ./cmd/rwkv-cli`。
  `dist/rwkv-cli` 是 2026-09-15 的旧产物，canonical 少三个轴，不得用于正式跑分。
- 记录 `git rev-parse HEAD` 与工作区是否干净；工作区不干净的跑分只能算探索。
- 凭据只走环境变量（`--api-header-env 'CF-Access-Client-Id=RWKV_CF_ID'` 等），
  **不写进任何入库文件、run 目录名或报告**。

## 3. 端点（rwkv_lightning_cuda）

后端文档：<https://github.com/Alic-Li/rwkv_lightning_cuda/blob/main/rwkv_lightning_api_doc.md>。

| 事项 | 规定 | 原因 |
|---|---|---|
| `--completion` | `rwkv-lightning-cuda` | — |
| `--api-url` | `https://api-7b.rwkvos.com/v1`（到 `/v1` 为止） | cuda 客户端自己拼路径；旧 python 版（`--completion rwkv-lightning`）才要完整路径 |
| `--api-stop-tokens` | **不传**：cuda 客户端自动发整数 EOS `[0]` | 文本 stop_tokens 在该后端上 HTTP 500；后端默认含 261（`\n\n`）会截断长 JSON |
| 并发 | 总计 **≤ 64**（workbank 48 + bfcl-product 16），且不超过 `hard_max_bsz` | hard_max_bsz（169）只按显存算；2026-09-23 关闭合并后约 168 个请求同时预填充，2 秒内约 115 路断流、随后约 7 分钟无响应。端点是共享的 |
| 模型身份 | 跑前、跑后各记一次 `/v1/models` 与 `/v1/server/status` | 请求里的 `model` 字段被忽略；端点曾静默从 g1i 换到 g1j |
| 截断判断 | 后端 `finish_reason` 恒为 `stop`，客户端按 token 数推断 `length` | 报告里"截断"是推断值，须注明 |

python 探针须设 `User-Agent: curl/8.7.1`，否则 Cloudflare 回裸 403。

## 4. 采样口径

**`top_k=1` 时温度不起作用**（2026-09-23 在 g1k 上实测：top_k=1 下 T=0.001 与 T=1.0 三次输出逐字相同）。
`rwkv-cli` 默认 `--temperature 1 --top-k 1`，即贪心。历史上所有写着 "T=0.3" 的 RWKV run 实际都是贪心。

采样用**命名预设**：`rwkv-cli --sampling <名字>`（`internal/samplingpreset`），显式 `--temperature` 等仍可覆盖单项；
`run.json` 的 `sampling.preset` 按实际生效的值反查记录（被覆盖过就记为空）。没有唯一最优，按任务选：

| 预设 | T | top_k | top_p | presence / frequency / decay | 用途（2026-09-23 g1k 扫参实测） |
|---|---|---|---|---|---|
| `greedy` | 1 | 1 | 1 | 0 / 0 / 1 | 回归与调试；最接近可复现（批处理仍有约 ±1 题抖动） |
| `g1k-agent` | 0.3 | 65536 | 0.5 | 0 / 0 / 1 | **默认**，工具调用决策；bfcl-product 最高（均 48/60） |
| `g1k-agent-fast` | 0.3 | 65536 | 0.5 | 0.5 / 0.1 / 0.996 | 长的多步 Agent 任务；与 g1k-agent 同分数带、快约 27%；presence 1.0 已掉分 |
| `g1k-stable` | 1 | 20 | 0.3 | 0 / 0 / 1 | 少副本的 A/B 对比；副本间波动最小 |
| `backend` | 1 | 20 | 0.3 | 2 / 0.2 / 0.996 | rwkv_lightning 作者默认；聊天与最快跑分（回复长度约减 60%） |

`top_k 65536` 是词表大小，表示不截断（CLI 不收 0）。**高温不截断不要用**：T 1.0 / top_p 1.0 时 bfcl-product 22/60。

- API 模型：不支持 `top_k`/`penalty_decay`，只用 `--temperature` 与 `--top-p`。
  **DeepSeek-flash 不能用 T=0**（五轮作废 14→40，见 `bench/workbank/reports/dsflash-baseline-2026-09-22.md` §2）；
  Qwen3.5-9B 在 workbank 上 T=0.3 比 T=0 高约 6pp。给没跑过的模型定参数前先翻 `runs/` 与报告。

## 5. 题库、预算与重复

**题库**：workbank 是主考卷（真 Agent 任务）；其余套件是辅助读数。

| 套件 | 调用 | 备注 |
|---|---|---|
| workbank 148 | `--cases bench/workbank/cases --tool-catalog work-v1 --file-tools lines --include-draft` | 主指标；另报 `reviewed` 子集 |
| bfcl-product 60 | `--suite bfcl-product` | 工具时机 |
| boundary 18 / assistant 6 / smoke 10 | `--suite …` | 在 `g1k` 下 boundary 历史为 0/18，是真实读数，不为它换格式 |
| primitive-orig30 / feedback30 | `--suite …`（不传 `--profile`） | 自带协议 |
| BFCL v4 抽样 491 | `scripts/bfcl.sh`（`configs/bfcl-sample-v2.json`） | 抽样对 live_multiple 高估约 12pp，只作同口径纵向比较 |

记录 `bank_version`（workbank cases 的 sha256）；题库改过的跑分不与旧分直接比。

**预算（所有模型统一）**：`--max-steps 16 --max-tokens 4096 --decision-max-tokens 2048 --case-timeout 30m`。
`--max-tokens` 只管最终回答；决策步不另给就落到协议默认 512。g1k 会无视格式自发 `<think>`（2026-09-23：142/148 题首步），
512 把一半思考截断成协议无效。自发思考视为模型缺陷不去修，只给 2048 的上限：正常思考能闭合，复读空转会被截停。
单题超时默认只有 2 分钟：2026-09-23 greedy 148 题并发时 56 题被 `context deadline exceeded` 掐断。
超时值记在 `run.json` 的 `harness.case_timeout_seconds`（2026-09-23 起），闸门检查。

**关闭客户端请求合并**：`--remote-batch-wait 0s`。默认 10ms 窗口把并发请求合成一个 batch，且整批响应结束才把结果交给各调用；
一条复读到上限的生成会拖住同批所有短回复（2026-09-23 实测每次调用约 4 分钟，25/148 题撞满 30 分钟）。CUDA 后端自己做并发批处理。
agent-eval 原本把窗口写死为 10ms，2026-09-23 起开放 `--remote-batch-wait` 并记入 `harness.remote_batch_wait_ms`，闸门检查。
历史上 g1k 用过 10 或 16 步、1024 token，Qwen 用 16 步、4096 token——预算不同的分数不可比。

**重复次数**：
- 采样档：k=3，报均值、极差、pass@3（任一次过）、pass^3（三次全过）。
- `greedy`：k=2。后端批推理有 ±1–2 题抖动，两次一致才算确定。
- 选择题（比如挑采样档）在 k=3 前，**先写下判定规则再跑**（§7）。

## 6. 有效性闸门（每个 run 跑完立刻查，任一不过即作废重跑）

1. `run.json` → `harness.wire_preset == "g1k"`（RWKV）；`model.completion` 与预期一致。
2. `sampling` 与档表逐项一致（特别是 `top_k`）。
3. `harness.max_steps == 16`，token 预算一致。
4. `len(case_ids)` 等于预期题数；跑前跑后 `/v1/models` 一致。
5. 作废题（`invalid_cases`）与传输错误（HTTP 5xx、`unexpected EOF`、TLS）单独列出：
   - 有基础设施错误的 run **整轮重跑**，不做逐题拼接（拼出来的 summary 不是 harness 产物，`replicate_summary.py` 也会拒收）。
   - 最后一次尝试仍有错误（可复现的上游故障，或上下文超长之类非传输作废）：保留该 run，**作废计为失败**，
     不从分母剔除，并在报告里标出。剔除会让"选错取数方式"的题从测量里消失。
   - 以上由 `.claude/skills/rwkv-bench/sweep.py` 自动执行（`--max-attempts`，默认 2）。

## 7. 统计与比较

- 主指标：workbank `task_success`，分母 = 全部题数（作废计失败）。同时报按 scenario / level 的拆分。
- 两个配置比较：只用**同一天、同一端点、同一 bank_version** 的成对 run；逐题配对，报翻转数（+a/−b）与符号检验 p 值。
  `bench/workbank/tools/compare.py` 做配对，`replicate_summary.py` 汇总 k 次，`capability_gate.py` 做失败分层
  （protocol / closeout / toolchoice / format / capability）——只有落到 capability 层的失败才算"模型不会"。
- 差距小于同配置 k 次极差的，结论写"无法区分"，不写"更好"。
- 预注册：选择型实验（采样档、格式候选）在跑前把"主指标 + 决胜规则 + 平局处理"写进该轮 PLAN.md。

## 8. 目录与落库

- run 目录：`runs/bench-YYYYMMDD/<model>-<suite>-<arm>-k<i>/`（`runs/` 不入库）。
- 入库只放源与结论：该轮 `docs/evaluations/<topic>-YYYYMMDD/PLAN.md` 与 `REPORT.md`，
  以及 `bench/workbank/ledger/` 的 ingest 行（`ledger.py ingest --config-name <model>-<arm> --k-index <i>`）。
- 报告必须包含：HEAD、二进制构建时间、端点快照（模型 id / engine_version / hard_max_bsz）、档表、
  题库版本、每个 run 的闸门结果、作废与重跑明细。

## 9. 坑的出处

| 坑 | 发生 | 记录 |
|---|---|---|
| 漏传 `--profile` 静默落 legacy | 2026-09-22 g1k 148 题 0/148 | `runs/workbank/rwkv-g1k-k0` |
| `top_k=1` 使温度失效 | 全部历史 RWKV run | 本文 §4 |
| DeepSeek 贪心崩溃 | 2026-09-21/22 | `dsflash-baseline-2026-09-22.md` §2 |
| 作废题剔出分母 | 2026-09-22 下架 4 题 | commit 88f07be |
| 端点静默换模型 | 2026-09-01 g1i→g1j | BFCL g1j 复跑记录 |
| 流式断流冤判约 12pp | BFCL c130 全量 | 同上；须重试合并 |
| 判分按 id 字符串排序错位 | BFCL 重判 | 同上；按 id 建 map |
| chat 路径 `wire_canonical` 失真 | 全部 API 模型 run | 本文 §1 |
| `dist/` 二进制过期 | 2026-09-23 发现 | 本文 §2 |
| python 版与 cuda 版端点参数不同（URL 形式、stop 形式） | 2026-09-23 探针 | 本文 §3；`runs/wire-check-20260918/api-contract-audit.json` |
| 关闭合并后 168 路同时预填充打挂共享端点 | 2026-09-23 greedy 102/148 作废 | 本文 §3；总并发 ≤ 64 |
| 客户端合并请求造成队头阻塞 | 2026-09-23 修复 4 MiB 后首档 25/148 撞满 30m | 本文 §5；`--remote-batch-wait 0s` |
| 合并请求的 4 MiB 上限按整批算，整批作废 | 2026-09-23 第三次首档 132/148；09-22 的 30 题同源 | 已修（batch 上限按条数放大） |
| `/v1/models` 的 `created` 是请求时刻 | 2026-09-23 | 不能据此判断后端重启 |
| 决策步预算默认 512，截断自发思考 | 2026-09-23 阶段 1 首档 85/148 协议无效 | 本文 §5；闸门查 `decision_max_output_tokens` |
| 单题超时默认 2 分钟，高并发下成批掐断 | 2026-09-23 阶段 1 首档 56/148 | 本文 §5；`sweep.py` 固定 30m |
| workbank 的 firstcall=auto 让 `--strict-spec` 误拒 | 2026-09-23 探针 | 已修：文本传输下 `MatchPreset` 忽略该惰性轴 |
