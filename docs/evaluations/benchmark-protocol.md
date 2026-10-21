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
  逐字节契约见 [`docs/design/corpus-g1k-wire-format.md`](../design/corpus-g1k-wire-format.md)。
- **不传 `--profile` 不会报错，而是静默落到 legacy 默认格式**（md-fence / 两阶段 / 带示例块）。
  2026-09-22 的 g1k 148 题就这样跑出 0/148、作废 30。`--strict-spec` 只拒绝未注册组合，挡不住"忘传"——
  所以跑后必须核对 `run.json` 的 `harness.wire_preset == "g1k"`（§6）。
- API 模型的对话模板由推理端负责，不是我们的事。注意：chat 路径下 `run.json` 的 `wire_canonical` 仍会写一串
  md-fence/legacy，**那是记录缺陷，实际未生效**；判断走的是哪条路径看 `model.completion`。
- 两个例外，保留各自的协议：
  - `primitive-orig30` / `primitive-feedback30`：套件自带 benchmark transcript（md-fence + `submit`）。
  - 官方 BFCL（`scripts/bfcl.sh`）：自有 MD 锚点 / XML 裸 / XML 锚点三档，不与 workbank 混比。

## 2. 二进制与环境

- **只用从当前 HEAD 编译的二进制**：`go build -o local/bin/rwkv-cli ./cmd/rwkv-cli`。
  `local/dist/rwkv-cli` 是 2026-09-15 的旧产物，canonical 少三个轴，不得用于正式跑分。
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
  **DeepSeek-flash 不能用 T=0**（五轮作废 14→40，见 `docs/workbank/reports/dsflash-baseline-2026-09-22.md` §2）；
  Qwen3.5-9B 在 workbank 上 T=0.3 比 T=0 高约 6pp。给没跑过的模型定参数前先翻 `local/runs/` 与报告。

## 5. 题库、预算与重复

**题库**：2026-10-15 起，主考卷是 **exam-full / exam-quick**（题数以 `bench/exam/SUITES.md` 为准，2026-10-15 为 378 / 76），按 App 默认配置考（`--harness app`，清单自带）。
构成、名词和覆盖缺口见 `bench/exam/SUITES.md`，来由见 `docs/evaluations/bench-composition-20261015/REPORT.md` §8～§10。

| 套件 | 调用 | 备注 |
|---|---|---|
| **exam-full** | `--cases bench/exam/full.json` | **主指标**。清单带 tool_catalog=agent-tool-v2.0、harness=app；预算、兜底、任务约定全部取 App 默认（16 步 / 4096 / 2048 / 兜底 2/3/3 / 暂存文件），CLI 的预算参数在这个模式下不生效 |
| **exam-quick** | `--cases bench/exam/quick.json` | 快速比较，不当作绝对水平；与完整版的排名一致性见 bench-composition 报告 §10.2 |
| 裸能力诊断 | 同上加 `--harness raw` | 兜底关闭，看模型自己会不会收尾；作为训练信号另报，不当主分 |
| 历史口径 workbank 148 | `--cases bench/workbank/cases --tool-catalog agent-tool-v1.0 --file-tools lines --include-draft` | 主指标；另报 `reviewed` 子集 |
| bfcl-product 60 | `--suite bfcl-product` | 工具时机 |
| boundary 18 / assistant 6 / smoke 10 | `--suite …` | 在 `g1k` 下 boundary 历史为 0/18，是真实读数，不为它换格式 |
| primitive-orig30 / feedback30 | `--suite …`（不传 `--profile`） | 自带协议 |
| BFCL v4 抽样 491 | `scripts/bfcl.sh`（`configs/bfcl-sample-v2.json`） | 抽样对 live_multiple 高估约 12pp，只作同口径纵向比较 |

记录 `bank_version`（workbank cases 的 sha256）；题库改过的跑分不与旧分直接比。
exam 跑分记录 `harness.exam_hash`：哈希不同的两次跑分不直接比。2026-10-15 的自然问法改写同时改了 workbank 题面，workbank 的新分数也不能与之前的分数直接比。
API 模型按 App 新建 chat 连接的口径跑：`--chat-thinking disabled`，不传 `--profile`（chat-completions 后端不套文本续写的 wire 预设）。

**预算（所有模型统一）**：`--max-steps 16 --max-tokens 4096 --decision-max-tokens 2048 --case-timeout 30m`。
`--max-tokens` 只管最终回答；决策步若落到协议默认 512，g1k 自发的 `<think>`（2026-09-23：142/148 题首步）会被截断一半成协议无效。
自发思考视为模型缺陷不去修，只给 2048 的上限：正常思考能闭合，复读空转会被截停。
2026-10-15 起这两项是 agent-eval 的默认值：`--profile g1k*` 未给 `--decision-max-tokens` 时取 2048（`g1k-think` 取 4096，与语料渲染一致），
`--case-timeout` 默认 30m（原 2 分钟，2026-09-23 greedy 148 题并发时 56 题被 `context deadline exceeded` 掐断）。显式传值仍然有效。
超时值记在 `run.json` 的 `harness.case_timeout_seconds`（2026-09-23 起），闸门检查。

**客户端请求合并（2026-10-15 起默认开启）**：agent-eval 默认 `--remote-batch-wait 20ms --remote-batch-max 64 --remote-batch-inflight 4`，
`bench sweep` 显式传这三个值（`--remote-batch-inflight` 可在 sweep 上改）；记入 `harness.remote_batch_wait_ms` / `remote_batch_max` /
`remote_batch_inflight`，闸门检查。
- 为什么开：rwkv_lightning **不做跨请求的连续批处理**。每个 HTTP 请求只把自己 `contents[]` 里的 prompt 组成一个 batch 跑到底
  （上游 `/v1/batch/completions` → `batch_generate_stream_with_state`），同一张卡上多个请求的解码循环轮流执行、不共享前向。
  2026-10-15 实测（7.2B fp16，详见 `remote-batch-throughput/REPORT.md`）：单卡一步 bsz=1 约 8–12 ms、bsz=64 约 15–23 ms，
  所以每卡吞吐只看**单个请求里有几行**：bsz=1 约 85–125 tok/s，bsz=64 约 2,700–4,100 tok/s；48 个单行请求并发总共只有约 280 tok/s。
- 怎么合：同时在跑的合并请求最多 `--remote-batch-inflight` 个（设成端点背后的卡数；8018 网关 3 卡，默认 4）。
  名额占满时新到的调用排队，等有请求结束就把队列整个作为一个更宽的请求发出；排队超过 2 秒则不等名额直接发
  （防止某个请求只剩一行在复读到上限、堵住队列）。20ms 窗口只负责把同一时刻到达的调用收齐。
  只有 20ms 窗口、不设在途上限时，稳态下调用到达率每秒不到 1 次，窗口里几乎凑不到第二条，合批名存实亡。
- 每行何时交付：命中文本停止串（`</tool_call>`、`\nUser:` 等）即刻交付；以 EOS 结束的行，服务端只是不再输出它
  （新旧引擎都到整批结束才发各行 `finish_reason`，跑满 max_tokens 也报 `stop`），客户端在同批其他行又走了 64 步、
  这一行仍无输出时判定它已结束并交付。所有行都交付后断开连接，服务端随之停止这个 batch。
- 决策、终答、压缩调用的 token 预算不同也合在一个请求里：请求按最宽的预算发，较窄的行在客户端按自己的预算截断（报 `length`）。
- **开/关合批的 run 不能混比**：批维度不同，fp16 数值有差异（2026-10-15 greedy 对照：第一次调用约 20% 文本不同，此后整题分叉）。
  `run check` 对记为 0 的旧 run 仍判 PASS，但标出 "unbatched run … do not pair it directly"；`run compare` 两边合批设置不同时在 stderr 警告。
- 合批参数改动时，同时改 `internal/continuation/rwkvlightning`（`DefaultBatchWait` / `DefaultBatchMax` / `DefaultBatchInflight`），sweep 与闸门自动跟随。
- 合批之后的瓶颈是**预填充**：agent 每步都把整段上下文重新预填充，workbank prompt 与生成 token 之比约 17–20 : 1。
  要再快，需要服务端做前缀状态复用（见 REPORT 的服务端建议），客户端无能为力。
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
   - 有基础设施错误的 run 用 `agent-eval --resume` **只重跑作废题与基础设施错误题**：合并由 harness 自己完成，
     续跑前核对运行配置签名（模型、wire、采样、adapter/state、预算、case 内容哈希等，见下方"断点续跑"），
     产物格式与一次跑完相同。仍然**不做手工逐题拼接**（拼出来的 summary 不是 harness 产物，`run replicate` 也会拒收）。
   - 最后一次尝试仍有错误（可复现的上游故障，或上下文超长之类非传输作废）：保留该 run，**作废计为失败**，
     不从分母剔除，并在报告里标出。剔除会让"选错取数方式"的题从测量里消失。
   - 以上由 `rwkv-lab bench sweep` 自动执行（`--max-attempts`，默认 2）。

**断点续跑**（`rwkv-cli agent-eval --resume`）：
- 运行中每题结束立刻追加到 `<output>.partial/cases.jsonl`（一行一题：`index`、`case_id`、`status`、`elapsed_ms`、
  `finished_at`、`result` = summary.json 里该题的 CaseResult、`trace` = 该题的 trace 记录；每行写完 fsync）；
  `progress.json` 记 `total/done/pass/fail/invalid/resumed`、开始时间与 `eta_seconds`/`eta_at`；`signature.json` 记 run_id、开始时间与配置签名。
  stderr 每题一行 `[done/total] case_id pass|fail|invalid 用时 eta 剩余`。ETA = 本次尝试已完成题数的吞吐外推剩余题数，
  本次完成不足 5 题时显示 `eta ?`；开头（先完成的是短题）和收尾（剩下的是慢题）会偏乐观。
- `--resume`：partial 存在且签名一致时，跳过已完成且非作废、非基础设施错误的题，只跑其余题，合并后写最终
  run.json / trace.jsonl / summary.json（run_id 与 started_at 沿用第一次尝试，`wall_time_millis` 含中断时间）。
  签名不一致即拒绝并逐项列出差异；只有 `case_parallelism` 允许改（OOM 后降并发是续跑的主要场景）。
  partial 不存在时 `--resume` 等同正常开跑。
- 不带 `--resume` 而 partial 已存在 → 拒绝运行，避免静默覆盖或混入旧结果。
- 被中断（SIGINT/SIGTERM）时不写最终产物（被切断的题不应计为失败），只保留 partial。
- 最终产物写完后：没有作废/基础设施错误题就删掉 partial；有则保留，供挪开成品目录后 `--resume` 只重跑这些题。

## 7. 统计与比较

- 主指标：exam-full 的 `task_success`，分母 = 全部题数（作废计失败）。同时按 `bench/exam/full.json` 里每题的 `task`（任务类型）、`difficulties`（难点）、`language` 出分能力面板；不要只报总分（总分曾被 web、notool 两类题左右，见 bench-composition 报告 §4.3）。
- 两个配置比较：只用**同一天、同一端点、同一 bank_version** 的成对 run；逐题配对，报翻转数（+a/−b）与符号检验 p 值。
  `bench/workbank/tools/compare.py` 做配对，`replicate_summary.py` 汇总 k 次，`capability_gate.py` 做失败分层
  （protocol / closeout / toolchoice / format / capability）——只有落到 capability 层的失败才算"模型不会"。
- 差距小于同配置 k 次极差的，结论写"无法区分"，不写"更好"。
- 预注册：选择型实验（采样档、格式候选）在跑前把"主指标 + 决胜规则 + 平局处理"写进该轮 PLAN.md。
- 耗时与 token：`rwkv-lab run cost <run_dir...> [--top N] [--json] [--no-recount]` 按墙钟耗时、整题累计生成 token、
  最大上下文、收尾时间各列 top N，并按 scenario / probe_axis 汇总；多个 run 同题取均值与最大值。
  - 字段来源：`summary.json` 的 `cases[].cost` 与 `turns[].cost`（墙钟 `wall_ms`、模型合计 `model_ms`、首 token 等待合计 `wait_ms`、工具合计 `tool_ms`、
    `steps`、`prompt_tokens`、`completion_tokens`、`max_prompt_tokens`、`token_source`、`hit_max_tokens` / `hit_max_steps` / `hit_timeout`）；
    每步 `usage` 带 `prompt_source` / `completion_source`。
  - RWKV（rwkv_lightning）端点不回 usage：completion 取流式 delta 数（chunk_size=1，一块一个 token，`server_stream`），
    prompt 用本地 World 词表计数（`local_vocab`，需要 `third_party/rwkv-mobile` 子模块）。
    预算逻辑只信端点自报的数，补上的计数不改变生成。
  - 旧产物没有 `cost`：从步骤时间戳回算耗时；缺的 token 数默认用本地词表从 `trace.jsonl` 回算（217 MB trace 约 3 秒；
    含路由调用，不含被客户端截掉的停止串，`token_source = local_vocab_trace`），`--no-recount` 则显示为 `—`。
  - `wait_ms` 是每步从发请求到首 token 的时间之和（合批窗口 + 端点排队 + prefill）。并发跑分时 `model_ms` 里大半可能是排队：
    `model_ms` 高而 `wait_ms` 低 = 题本身生成得长；`wait_ms` 高 = 端点堵。
  - rwkv_lightning 跑满 `max_tokens` 时也回 `finish_reason: stop`，所以 `hit_max_tokens` 不看 finish，
    而看单次调用生成数是否 ≥ 该次请求上限的 98%（流式计数会漏掉半个多字节字符的 token，留 2% 余量）；回算旧产物时同样按 trace 判定。
    长尾题基本都是复读到上限，先看这一列。

## 8. 目录与落库

- run 目录：`local/runs/bench-YYYYMMDD/<model>-<suite>-<arm>-k<i>/`（`local/runs/` 不入库）。
- 入库只放源与结论：该轮 `docs/evaluations/<topic>-YYYYMMDD/PLAN.md` 与 `REPORT.md`，
  以及 `bench/workbank/ledger/` 的 ingest 行（`ledger.py ingest --config-name <model>-<arm> --k-index <i>`）。
- 报告必须包含：HEAD、二进制构建时间、端点快照（模型 id / engine_version / hard_max_bsz）、档表、
  题库版本、每个 run 的闸门结果、作废与重跑明细。

## 9. 坑的出处

| 坑 | 发生 | 记录 |
|---|---|---|
| 漏传 `--profile` 静默落 legacy | 2026-09-22 g1k 148 题 0/148 | `local/runs/workbank/rwkv-g1k-k0` |
| `top_k=1` 使温度失效 | 全部历史 RWKV run | 本文 §4 |
| DeepSeek 贪心崩溃 | 2026-09-21/22 | `dsflash-baseline-2026-09-22.md` §2 |
| 作废题剔出分母 | 2026-09-22 下架 4 题 | commit 88f07be |
| 端点静默换模型 | 2026-09-01 g1i→g1j | BFCL g1j 复跑记录 |
| 流式断流冤判约 12pp | BFCL c130 全量 | 同上；须重试合并 |
| 判分按 id 字符串排序错位 | BFCL 重判 | 同上；按 id 建 map |
| chat 路径 `wire_canonical` 失真 | 全部 API 模型 run | 本文 §1 |
| `local/dist/` 二进制过期 | 2026-09-23 发现 | 本文 §2 |
| python 版与 cuda 版端点参数不同（URL 形式、stop 形式） | 2026-09-23 探针 | 本文 §3；`local/runs/wire-check-20260918/api-contract-audit.json` |
| 关闭合并后 168 路同时预填充打挂共享端点 | 2026-09-23 greedy 102/148 作废 | 本文 §3；总并发 ≤ 64 |
| 客户端合并请求造成队头阻塞 | 2026-09-23 修复 4 MiB 后首档 25/148 撞满 30m | 已修（逐条按停止串提前交付）；EOS 行仍等整批，见 §5 |
| 关闭合并后吞吐被 bsz=1 带宽卡死（服务端无连续批处理） | 2026-10 每节点约 50 次调用/分，并发 78→256 不增；只有 20ms 窗口时稳态凑不到批 | 本文 §5；默认在途 4 / 单批 64 / 窗口 20ms |
| 合并请求的 4 MiB 上限按整批算，整批作废 | 2026-09-23 第三次首档 132/148；09-22 的 30 题同源 | 已修（batch 上限按条数放大） |
| `/v1/models` 的 `created` 是请求时刻 | 2026-09-23 | 不能据此判断后端重启 |
| 决策步预算默认 512，截断自发思考 | 2026-09-23 阶段 1 首档 85/148 协议无效 | 本文 §5；闸门查 `decision_max_output_tokens` |
| 单题超时默认 2 分钟，高并发下成批掐断 | 2026-09-23 阶段 1 首档 56/148 | 本文 §5；`sweep.py` 固定 30m |
| workbank 的 firstcall=auto 让 `--strict-spec` 误拒 | 2026-09-23 探针 | 已修：文本传输下 `MatchPreset` 忽略该惰性轴 |
| md-fence 解析器把终答在第一个围栏处截断 | 2026-09-22 dsflash 基线 18 次终答被切，`code-0008` 因此判失败（`scr-0016` 3134→138 字符） | 已修（harness **v22**，`internal/agent/g1_functions_parser.go`：围栏只在包工具调用时才是信封）。**v21 及更早的 API 模型分数不能与 v22 直接比较**；学生 g1k 走 xml 解析器不受影响 |
