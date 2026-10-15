---
name: rwkv-bench
description: 在 RWKV-Agent 仓库里做正式跑分的检查单——RWKV 模型（rwkv_lightning 端点）或 API 模型（Qwen/DeepSeek 等）跑 workbank、bfcl-product、boundary、primitive 或 BFCL 时使用。用户说"跑分""测一下 g1k""基准测试""横测""A/B""换个温度试试""和 Qwen 比一下"，或要比较两个模型/state/采样/格式配置时，一定要用。只是调试单道题、看 trace 时不用。
---

# rwkv-bench：正式跑分检查单

规程全文：`docs/evaluations/benchmark-protocol.md`。本 skill 是执行顺序；每一步都有它防的坑，不要跳。

## 0. 先想清楚要回答什么

写下：被测对象、对照组、主指标（默认 workbank strict task_success）、判定规则。
这是选择型实验（挑采样档、挑格式）时，把这些写进 `docs/evaluations/<topic>-YYYYMMDD/PLAN.md` **再**开跑。
先翻 `local/runs/` 和 `docs/workbank/reports/` 看这个模型/端点以前怎么跑的——DeepSeek 贪心崩溃那次，
证据早就在 `local/runs/` 里，没人翻。

## 1. 二进制

```bash
go build -o local/bin/rwkv-cli ./cmd/rwkv-cli && go build -o local/bin/rwkv-lab ./cmd/rwkv-lab && git rev-parse HEAD && git status --short
```

只用 `local/bin/rwkv-cli`。`local/dist/rwkv-cli` 是旧产物。工作区不干净 → 这次只能算探索，报告里注明。

## 2. 端点快照（RWKV）

凭据从用户处拿，只放环境变量（`RWKV_CF_ID` / `RWKV_CF_SECRET`），不写进文件：

```bash
curl -sS https://api-7b.rwkvos.com/v1/models -H "CF-Access-Client-Id: $RWKV_CF_ID" -H "CF-Access-Client-Secret: $RWKV_CF_SECRET"
curl -sS https://api-7b.rwkvos.com/v1/server/status -H "CF-Access-Client-Id: $RWKV_CF_ID" -H "CF-Access-Client-Secret: $RWKV_CF_SECRET"
```

记下模型 id、`engine_version`、`prefill_queue.hard_max_bsz`。**总并发默认 64**（`rwkv-lab bench sweep --max-concurrency`）：
hard_max_bsz 只按显存算，2026-09-23 约 168 个请求同时预填充把这个共享端点打挂过。
**跑完再拍一次**，模型 id 变了整轮作废（端点会被静默换模型）。

state 上传：**走 Cloudflare**（`rwkv-cli state upload --api-url https://api-7b.rwkvos.com/v1` 加两个 `--api-header-env`），串行上传，每个约 21 秒；推理照旧直连 `http://100.64.0.4:8018/v1`，两条路是同一个部署。
2026-10-13 起，直连 Tailscale 链路一遇到超过约 1 MB 的请求体就会卡死，还会让整条隧道假死十几秒；小请求不受影响。
`RWKV_CLI=<路径>` 可以让 sweep 使用固定版本的 cli，不必替换 `local/bin/rwkv-cli`。

## 3. 命令模板

RWKV（workbank）：

```bash
./local/bin/rwkv-cli agent-eval \
  --completion rwkv-lightning-cuda --model <模型id> \
  --api-url https://api-7b.rwkvos.com/v1 \
  --api-header-env 'CF-Access-Client-Id=RWKV_CF_ID' --api-header-env 'CF-Access-Client-Secret=RWKV_CF_SECRET' \
  --profile g1k --strict-spec \
  --cases bench/workbank/cases --tool-catalog work-v1 --file-tools lines --include-draft \
  --max-steps 16 --max-tokens 4096 --decision-max-tokens 2048 --case-parallelism 48 --case-timeout 30m \
  <采样档参数> \
  --output local/runs/bench-YYYYMMDD/<model>-workbank-<arm>-k<i>
```

内置套件把 `--cases … --include-draft` 换成 `--suite bfcl-product|boundary|assistant|smoke`。
primitive 两套：`--suite primitive-orig30|primitive-feedback30`，**不传** `--profile`（套件自带协议）。

cuda 后端：`--api-url` 只写到 `/v1`，**不传** `--api-stop-tokens`（客户端自动发整数 EOS；文本形式会 500）。
旧记忆里的 `…/v1/batch/completions` 完整路径和 `--api-stop-tokens cuda` 属于 python 版后端，新二进制已不接受 `cuda`。

API 模型：`--completion chat-completions`，不传 `--profile`、`--api-stop-tokens`；对话模板由推理端负责。

**`--decision-max-tokens 2048` 必须给**：不给就落到协议默认 512，g1k 自发思考会被截断成协议无效。
**合批用默认值，不要再给 `--remote-batch-wait 0s`**（2026-10-15 起）：agent-eval 默认 `--remote-batch-wait 20ms --remote-batch-max 32`，
把同一时刻到达的调用合进一个 `/v1/batch/completions` 的 `contents[]`。rwkv_lightning **没有跨请求连续批处理**，
每个请求只跑自己的 contents[]；关掉合批时 N 路并发 = N 个 bsz=1 循环，被显存带宽卡在约 125 次前向/秒/卡
（7.2B fp16 约 14.4 GB 权重 / 1.8 TB/s），并发加到 256 也只是排队变长。命中 `\nUser:` 等文本停止串的调用本地即刻交付；
以 EOS 结束的调用要等同批最长的一条（服务端整批结束才报 finish_reason），所以单批设上限 32。
**开/关合批的 run 不能混比**：批维度不同，fp16 数值可能有微小差异；`run compare` 遇到两边合批设置不同会警告。
**`--case-timeout 30m` 必须给**：默认 2 分钟，高并发下大批题被计时器掐断（报 `context deadline exceeded`）。

采样用命名预设 `--sampling <名字>`，不要手拼六个数（**`--top-k 1` 会让温度失效**）：

| 预设 | 用途 |
|---|---|
| `greedy` | 回归、调试 |
| `g1k-agent` | 默认；工具调用决策 |
| `g1k-agent-fast` | 长的多步任务，快约 27% |
| `g1k-stable` | 少副本 A/B，波动最小 |
| `backend` | 后端默认，最快 |

数值见规程 §4；`rwkv-lab run check --arm <预设名>` 会核对 `run.json` 的 `sampling.preset`。扫参网格档（`t03-p05` 等）仍在 `internal/lab/runs/check.go` 的 `Arms` 表里。

API 模型只给 `--temperature` / `--top-p`。DeepSeek-flash 禁用 T=0。

重复：采样档 k=3，`greedy` k=2。

## 3.5 批量扫描：用脚本，不要手拼命令

```bash
export RWKV_CF_ID=… RWKV_CF_SECRET=…
local/bin/rwkv-lab bench sweep --out local/runs/bench-YYYYMMDD --arms greedy,t03-p10 \
  --suites workbank,bfcl-product --k 0 --dry-run      # 先看命令
local/bin/rwkv-lab bench sweep --out local/runs/bench-YYYYMMDD --arms greedy,t03-p10 \
  --suites workbank,bfcl-product --k 0                # 真跑；--k 0-2 跑三个副本
local/bin/rwkv-lab bench rank local/runs/bench-YYYYMMDD --save <rank.md>
```

`bench sweep` 做的事：端点前后快照、每档开跑前核对模型 id、同档多套件在 bsz 预算内并行、每个 run 自动过闸门、
写 `experiment.json`（二进制 sha、git HEAD、diff sha、case 源 sha，供 `run replicate` 使用）。
- 只有写了 `experiment.json` 且 `gate_passed: true` 的 run 才算完成。
- 逐题断点：agent-eval 每题结束立刻把结果追加进 `<run>.partial/cases.jsonl`（fsync），日志里每题一行
  `[done/total] case_id pass|fail|invalid 用时 eta 剩余`，`<run>.partial/progress.json` 是实时计数和 `eta_at`
  （按本次吞吐外推，开头和收尾偏乐观）。
  进程被杀/节点 OOM 后重开同一条 sweep 命令即可：sweep 一律带 `--resume`，已完成的题不重跑，旧日志挪进 `aborted/`。
- 闸门 FAIL（参数配错）→ 立即中止，不重试。`RESUME REFUSED`（partial 是另一套配置留下的）同样中止，
  按提示修配置或删掉 `<run>.partial` 重来。
- 基础设施错误（invalid、5xx、超时等）→ 只重跑这些题（`--resume`，默认最多 2 次尝试）；最后一次仍有错就保留、
  作废计失败、标 `accepted_with_infra_errors`。

`bench rank` 按 PLAN 的预注册规则出排名（阶段 1 综合分、阶段 2 workbank 均值与极差平局规则、地板规则），并给出对照 greedy 的逐题翻转与符号检验。
新增采样档：只改 `internal/lab/runs/check.go` 的 `Arms` 表，sweep 与 rank 自动跟随。

## 4. 每个 run 跑完立刻过闸门

```bash
local/bin/rwkv-lab run check <run_dir> --arm <档> [--rwkv] [--primitive] --cases <题数>
```

任一 FAIL → 这个 run 作废，修参数重跑，不要"先看看分数"。它会查：`wire_preset == g1k`、采样逐项、
步数、终答与决策 token 预算、单题超时、请求合并窗口（RWKV 须为 20ms + 单批上限 32；旧 run 记为 0 也判 PASS，
但会提示"不可与合批 run 直接配对"）、题数，并给出 strict 分（作废计失败）。

`invalid` 不为 0 时，分清两类：
- 传输错误（5xx、`unexpected EOF`、TLS）：`bench sweep` 已自动用 `--resume` 重跑这些题；手动跑时把成品目录挪开，
  用原命令加 `--resume` 重跑（partial 目录在有作废/基础设施错误时会保留），由 agent-eval 自己合并出新产物。
  不要手工拼接 summary。
- 非传输作废（如上下文超长 400）：计为失败，保留。

## 5. 汇总与比较

```bash
local/bin/rwkv-lab run replicate <k 个 run 目录> --k 3 --out <out.json>
local/bin/rwkv-lab run compare <run A> <run B>
local/bin/rwkv-lab run gate <run 目录…> --label <名字>
local/bin/rwkv-lab run ledger ingest --config-name <model>-<arm> --k-index <i> <run_dir>
local/bin/rwkv-lab run cost <run 目录…> --top 20 [--json]
```

- `run cost` 看哪些题最费时间、最费 token、上下文最长、最后收尾（长尾题拖整轮时先看这个）；
  旧产物没有 token 数时自动用本地词表从 trace 回算（`--no-recount` 关闭）。
  `limits` 列的 max_tokens = 复读到上限（端点此时也报 stop，按生成数判定）；`wait s` 高说明是端点排队，不是题慢。

- 比较只用同一天、同端点、同 bank_version 的成对 run；报翻转 +a/−b 与符号检验 p。
- 差距小于同配置 k 次极差 → 写"无法区分"。
- 失分先过 `local/bin/rwkv-lab run gate` 分层：只有 capability 层才算"模型不会"，其余是协议、收尾、选工具或格式问题。

## 6. 报告

写 `docs/evaluations/<topic>-YYYYMMDD/REPORT.md`，必须包含：HEAD 与二进制构建时间、端点前后快照、
档表、bank_version、每个 run 的闸门结果、作废与重跑明细、strict 分（均值/极差/pass@k/pass^k）、
按 scenario/level 拆分、配对比较。`local/runs/` 不入库；凭据不出现在任何入库文件里。
