---
name: rwkv-bench
description: 在 RWKV-Agent 仓库里做正式跑分的检查单——RWKV 模型（rwkv_lightning 端点）或 API 模型（Qwen/DeepSeek 等）跑 workbank、bfcl-product、boundary、primitive 或 BFCL 时使用。用户说"跑分""测一下 g1k""基准测试""横测""A/B""换个温度试试""和 Qwen 比一下"，或要比较两个模型/state/采样/格式配置时，一定要用。只是调试单道题、看 trace 时不用。
---

# rwkv-bench：正式跑分检查单

规程全文：`docs/evaluations/benchmark-protocol.md`。本 skill 是执行顺序；每一步都有它防的坑，不要跳。

## 0. 先想清楚要回答什么

写下：被测对象、对照组、主指标（默认 workbank strict task_success）、判定规则。
这是选择型实验（挑采样档、挑格式）时，把这些写进 `docs/evaluations/<topic>-YYYYMMDD/PLAN.md` **再**开跑。
先翻 `runs/` 和 `bench/workbank/reports/` 看这个模型/端点以前怎么跑的——DeepSeek 贪心崩溃那次，
证据早就在 `runs/` 里，没人翻。

## 1. 二进制

```bash
go build -o bin/rwkv-cli ./cmd/rwkv-cli && git rev-parse HEAD && git status --short
```

只用 `bin/rwkv-cli`。`dist/rwkv-cli` 是旧产物。工作区不干净 → 这次只能算探索，报告里注明。

## 2. 端点快照（RWKV）

凭据从用户处拿，只放环境变量（`RWKV_CF_ID` / `RWKV_CF_SECRET`），不写进文件：

```bash
curl -sS https://api-7b.rwkvos.com/v1/models -H "CF-Access-Client-Id: $RWKV_CF_ID" -H "CF-Access-Client-Secret: $RWKV_CF_SECRET"
curl -sS https://api-7b.rwkvos.com/v1/server/status -H "CF-Access-Client-Id: $RWKV_CF_ID" -H "CF-Access-Client-Secret: $RWKV_CF_SECRET"
```

记下模型 id、`engine_version`、`prefill_queue.hard_max_bsz`。并发 `--case-parallelism` 不超过 hard_max_bsz。
**跑完再拍一次**，模型 id 变了整轮作废（端点会被静默换模型）。

## 3. 命令模板

RWKV（workbank）：

```bash
./bin/rwkv-cli agent-eval \
  --completion rwkv-lightning-cuda --model <模型id> \
  --api-url https://api-7b.rwkvos.com/v1 \
  --api-header-env 'CF-Access-Client-Id=RWKV_CF_ID' --api-header-env 'CF-Access-Client-Secret=RWKV_CF_SECRET' \
  --profile g1k --strict-spec \
  --cases bench/workbank/cases --tool-catalog work-v1 --file-tools lines --include-draft \
  --max-steps 16 --max-tokens 4096 --case-parallelism 148 \
  <采样档参数> \
  --output runs/bench-YYYYMMDD/<model>-workbank-<arm>-k<i>
```

内置套件把 `--cases … --include-draft` 换成 `--suite bfcl-product|boundary|assistant|smoke`。
primitive 两套：`--suite primitive-orig30|primitive-feedback30`，**不传** `--profile`（套件自带协议）。

cuda 后端：`--api-url` 只写到 `/v1`，**不传** `--api-stop-tokens`（客户端自动发整数 EOS；文本形式会 500）。
旧记忆里的 `…/v1/batch/completions` 完整路径和 `--api-stop-tokens cuda` 属于 python 版后端，新二进制已不接受 `cuda`。

API 模型：`--completion chat-completions`，不传 `--profile`、`--api-stop-tokens`；对话模板由推理端负责。

采样档参数（**`--top-k 1` 会让温度失效**，所以非贪心档一定显式给 top-k）：

| 档 | 参数 |
|---|---|
| `greedy` | `--temperature 1 --top-k 1 --top-p 1` |
| `t03` | `--temperature 0.3 --top-k 65536 --top-p 1` |
| `backend` | `--temperature 1 --top-k 20 --top-p 0.3 --presence-penalty 2 --frequency-penalty 0.2 --penalty-decay 0.996` |
| `backend-nopen` | `--temperature 1 --top-k 20 --top-p 0.3` |

API 模型只给 `--temperature` / `--top-p`。DeepSeek-flash 禁用 T=0。

重复：采样档 k=3，`greedy` k=2。

## 3.5 批量扫描：用脚本，不要手拼命令

```bash
export RWKV_CF_ID=… RWKV_CF_SECRET=…
python3 .claude/skills/rwkv-bench/sweep.py --out runs/bench-YYYYMMDD --arms greedy,t03-p10 \
  --suites workbank,bfcl-product --k 0 --dry-run      # 先看命令
python3 .claude/skills/rwkv-bench/sweep.py --out runs/bench-YYYYMMDD --arms greedy,t03-p10 \
  --suites workbank,bfcl-product --k 0                # 真跑；--k 0-2 跑三个副本
python3 .claude/skills/rwkv-bench/rank.py runs/bench-YYYYMMDD --save <rank.md>
```

`sweep.py` 做的事：端点前后快照、每档开跑前核对模型 id、同档多套件在 bsz 预算内并行、每个 run 自动过闸门、
写 `experiment.json`（二进制 sha、git HEAD、diff sha、case 源 sha，供 `replicate_summary.py` 使用）。
- 只有写了 `experiment.json` 且 `gate_passed: true` 的 run 才算完成；中断留下的半成品下次自动挪进 `aborted/` 重跑，可随时断点续跑。
- 闸门 FAIL（参数配错）→ 立即中止，不重试。
- 基础设施错误 → 整轮重跑（默认最多 2 次）；最后一次仍有错就保留、作废计失败、标 `accepted_with_infra_errors`。

`rank.py` 按 PLAN 的预注册规则出排名（阶段 1 综合分、阶段 2 workbank 均值与极差平局规则、地板规则），并给出对照 greedy 的逐题翻转与符号检验。
新增采样档：只改 `check_run.py` 的 `ARMS`，两个脚本自动跟随。

## 4. 每个 run 跑完立刻过闸门

```bash
python3 .claude/skills/rwkv-bench/check_run.py <run_dir> --arm <档> [--rwkv] [--primitive] --cases <题数>
```

任一 FAIL → 这个 run 作废，修参数重跑，不要"先看看分数"。它会查：`wire_preset == g1k`、采样逐项、
步数与 token 预算、题数，并给出 strict 分（作废计失败）。

`invalid` 不为 0 时，分清两类：
- 传输错误（5xx、`unexpected EOF`、TLS）：同配置只重跑这些题（`--case <id>` 可重复）到新目录，合并后再判分。
- 非传输作废（如上下文超长 400）：计为失败，保留。

## 5. 汇总与比较

```bash
python3 bench/workbank/tools/replicate_summary.py <k 个 run 目录> --k 3 --out <out.md>
python3 bench/workbank/tools/compare.py <run A> <run B>
python3 bench/workbank/tools/capability_gate.py <run 目录…> --label <名字>
python3 bench/workbank/tools/ledger.py ingest --config-name <model>-<arm> --k-index <i> <run_dir>
```

- 比较只用同一天、同端点、同 bank_version 的成对 run；报翻转 +a/−b 与符号检验 p。
- 差距小于同配置 k 次极差 → 写"无法区分"。
- 失分先过 `capability_gate.py` 分层：只有 capability 层才算"模型不会"，其余是协议、收尾、选工具或格式问题。

## 6. 报告

写 `docs/evaluations/<topic>-YYYYMMDD/REPORT.md`，必须包含：HEAD 与二进制构建时间、端点前后快照、
档表、bank_version、每个 run 的闸门结果、作废与重跑明细、strict 分（均值/极差/pass@k/pass^k）、
按 scenario/level 拆分、配对比较。`runs/` 不入库；凭据不出现在任何入库文件里。
