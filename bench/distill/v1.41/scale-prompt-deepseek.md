# 给执行 Agent 的提示：v1.41 放量（DeepSeek 老师，保留思考）

> 用法：把下面「---」之间的整段原样交给执行 Agent。它在本机仓库根目录 `/Users/no22/Projects/RWKV-Agent` 工作。
> 凭据在本机 `/Users/no22/.llm_api_key.sh`，提示里只引用这个文件，不含 key 本身。

---

你在 RWKV-Agent 仓库里做 v1.41 蒸馏数据的**放量**：先出新题，再让老师模型在真实 harness 里把题做出来，最后渲染成可训练的行。
规格、流水线、样板都已就绪，你的工作是**照样板放量，不是重新设计**。

本提示是 `bench/distill/v1.4/b10-scale-prompt.md` 的覆盖层。那份文件是基础流程，本提示没提到的地方一律照它执行；两者冲突时以本提示为准。
与那份相比，主要变化有两个：老师换成 DeepSeek-flash，并且**保留思考**；目录和脚本按 2026-10-10 的新结构放。

## 0. 先读，按顺序（读完再动手）

1. `bench/distill/README.md`：目录结构和各版本状态。题目、老师脚本、报告都按版本放。
2. `bench/distill/v1.4/b10-scale-prompt.md`：基础流程，§0–§7 全读。§7 是 b12 的差别。
3. `bench/distill/v1.4/distill-allocation-v1.4.md` 和 `bench/distill/v1.41/distill-allocation-v1.41.md`：题类规格是最高权威。
4. `bench/distill/v1.4/reports/b10-pilot.md` §5–§6：试跑踩过的坑和放量口径。
5. `docs/evaluations/deepseek-teacher-20261010/REPORT.md` 和 `think-vs-g1k.md`：这个老师的分数、接口限制、思考长什么样。
6. `bench/distill/tools/README.md`：脚本放哪、怎么复用。

**不得读**的范围照 b10-scale-prompt §0（`bench/workbank/cases*`、`bench/holdout/`、`docs/workbank/reports/`、`bench/workbank/reports-data/`、`bench/workbank/ledger/`、`local/runs/` 下的**跑分** trace）。
例外：你自己这次产生的 `local/runs/distill/v141/` 可以读。

## 1. 范围与顺序

| 批次 | 内容 | 题放哪 | 报告放哪 |
| --- | --- | --- | --- |
| b10a | M2 查不到 + M3 不调工具 / 反问（约 120–150 题） | `bench/distill/v1.4/cases/` | `bench/distill/v1.4/reports/b10a.md` |
| b10b、b10c… | M4–M8（约 550 题） | 同上 | 同上 |
| b12a、b12b… | M9 bash、M10 专用工具（约 330 题，ID 从 9021 起） | `bench/distill/v1.41/cases/` | `bench/distill/v1.41/reports/` |

配额、ID 起点、中文下限照 b10-scale-prompt §1 和 v1.41 §2。

**第一批 b10a 走完 S1→S7 后停下来**，把报告交给用户确认，再开下一批。理由：老师换了，第一批的 pass@3、0/3 比例、思考统计要先过目。

## 2. 出题（S1–S2）

- 照 b10-scale-prompt §2 的硬规则。样板是 `bench/distill/v1.4/cases/*/*-80xx`、`bench/distill/v1.41/cases/*/*-90xx`。
- **脚本不复制**：每批建一个 `bench/distill/tools/b<批号>/`（如 `tools/b10a/`），里面的 `common.py` 只写几行批次设置：
  ```python
  import os, sys
  sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
  from casegen import Batch  # noqa: E402
  write_case = Batch(salt="b10a", author="llm:<你的模型名>-b10a", version="v1.4").write_case
  ```
  b12 批加上 `tool_catalog="work-v2"`，并从 `casegen` 引入 `Sidecar, check_reference, lines, weather`（照 `tools/b12/common.py`）。
  题目内容写在 `m*.py` 里。不得复制 `tools/b10/` 或 `tools/b12/` 的 `common.py`；`casegen.py` 缺功能就加参数，并保证 b10、b12 两批重跑后逐字节不变。
- 闸门：`bench/distill/tools/gate.sh v1.4 '*-8[0-9][0-9][0-9]'`（lint + verify 含破坏测试），加上 b10-scale-prompt §4 的五面去污染、dedup、hitcheck。
  b12 另加 `--test bench/bashprobe/cases` 一面，bash 参考解必须在 sidecar 里跑通。

## 3. 老师解题（S4–S5）

### 3.1 凭据（硬约束）

```bash
source /Users/no22/.llm_api_key.sh     # 导出 API_BASE、API_KEY、MODEL_NAME（deepseek-flash）
```

- 命令行只写 `--api-url "$API_BASE" --model "$MODEL_NAME" --api-key-env API_KEY`。
- **key 不得出现在任何文件、报告、日志、提交、对话输出里**。不要 `echo`、`cat`、`env` 这个文件或变量。
- 端点是 next-token.cc 的中转，同一个 key 下另有 `deepseek-v4-flash`、`deepseek-v4-pro`，**只用 `$MODEL_NAME`**。

### 3.2 二进制

开工时用当前 main 编一次，记下 sha256，之后全程不再重编：

```bash
go build -tags chatcompletions -o local/bin/rwkv-cli ./cmd/rwkv-cli
go build -o local/bin/rwkv-lab ./cmd/rwkv-lab
shasum -a 256 local/bin/rwkv-cli
```

必须在提交 `332beaa` 或之后编。从这个提交起，`corpus paths` 会把老师每步的思考写进脚本的 `reasoning` 字段；
更早的 `rwkv-cli` 解码脚本时会拒收这个字段，渲染直接失败（报 `agent-eval produced no trace`）。

### 3.3 命令

参数照 `common/distill-workflow.md` S4，下面几项是这次固定的：

```bash
local/bin/rwkv-cli agent-eval \
  --completion chat-completions --api-url "$API_BASE" --model "$MODEL_NAME" --api-key-env API_KEY \
  --temperature 0.3 --top-p 1 \
  --tool-catalog work-v1 --file-tools lines \
  --max-steps 16 --max-tokens 4096 --decision-max-tokens 8192 \
  --case-parallelism 8 --case-timeout 30m --remote-batch-wait 0s \
  --chat-system-suffix bench/distill/v1.4/teacher/b10-suffix.txt \
  --cases <本批题目的临时目录> --include-draft \
  --output local/runs/distill/v141/$B/teacher-k$k
```

- **思考保持默认（`--chat-thinking auto`）**：端点会返回 `reasoning_content`，harness 逐步记录。不得传 `--chat-thinking disabled`。
- **温度只能 >0**：T=0 时这个模型会大面积作废，沿用 0.3。
- **并发**：每个 run 8，同时最多两个 run（合计 16）。这个端点 16 并发实测不限流；出现 429 就降到 4，并只重跑 429 的题。
- **只跑本批新题**：把本批题目复制到临时目录（保持 `<场景>/<题号>/` 两层），用 `--cases` 指过去。
  不要直接用 `--cases bench/distill`：这样会把全库 1600 多题都跑一遍，浪费钱。
- b12 批：`--tool-catalog work-v2 --chat-system-suffix bench/distill/v1.41/teacher/b12-suffix.txt`，先跑 `scripts/build-justbash.sh` 编出 sidecar。
- 每题 k=3（`k=0,1,2` 三个输出目录）。传输错误（5xx、EOF、TLS、429）用同配置单题重跑，再合并；非传输作废（例如工具参数不是合法 JSON）计为失败。
- **若出现 `HTTP 400 … Thinking mode does not support this tool_choice`，立即停下报告用户**，不要关掉思考绕过去。workbank 同款 harness 不会发 `tool_choice: required`，出现了就说明配置不对。

### 3.4 第 0 步冒烟（放量前必做）

用 b10-pilot 的 70 道样板和 b12 的 20 道样板，k=1，**加 suffix 和不加 suffix 各跑一遍**，比较三项：
- pass 数；
- `b10_check.py` 的形态问题数；
- 思考统计（见 §3.6）。

加 suffix 应当不差于不加；明显更差就停下报告用户，不要自己改 suffix 的规则口径。结果写进 b10a 报告。

### 3.5 抽路径（必须确认思考保住了）

```bash
local/bin/rwkv-lab corpus paths --run local/runs/distill/v141/$B/teacher-k0 --run …k1 --run …k2 \
  --out bench/distill/v1.4/teacher/$B.jsonl --report local/runs/distill/v141/$B/paths-report.jsonl
```

- b12 批的脚本写到 `bench/distill/v1.41/teacher/$B.jsonl`。
- 抽完马上检查：脚本里有思考的输出占比，应在 60% 以上（筛选时 DeepSeek 是 69% 的步有思考）。是 0 就说明二进制太旧，停下修好再继续。
- `local/runs/distill/v141/` 下的老师 run 目录不入库，**但不得删除**：trace 里存着完整的思考和请求，以后渲染带思考版要用。
- 0/3 分诊、`b10_check.py`、逐条读终答，三层质检照 b10-scale-prompt §3 S5 做，不得省略。

### 3.6 思考统计（每批报告必带，先只统计、不按思考过滤）

对本批通过的路径，统计以下几项，统计口径照 `docs/evaluations/deepseek-teacher-20261010/think_compare.py`：
- 有思考的步占比；
- 首步、后续步的思考长度 p50 / p90；
- 超过 900 字符的步占比；
- 含 `Wait` / `Hmm` / `Actually` 的步占比；
- 中文题里用中文思考的占比。

现在**不要因为思考长或带 Wait 就丢路径**：带思考版怎么过滤还没定，用户会看完这些数再定。
只因终答、动作有问题才剔除（写进 `common/exclude.jsonl`）。

## 4. 渲染与验收（S6–S7）

- 这次只渲染**剔思考版**，即现行 g1k 格式。渲染会忽略 `reasoning` 字段，`wire_hash` 必须仍是 `707c67403b1b…`。
  命令照 b10-scale-prompt §4，`--cases bench/distill`（全库根，加载器会跳过 `cases-shelved`）。
- **不要实现**带思考版渲染（think-full profile）。那是下一步的事，等用户看完思考统计再定格式。
- 报告格式照 `b10-pilot.md`，另加 §3.6 的思考统计、第 0 步冒烟结果、老师 run 目录路径。报告里的每个数字都要能从产物复算。
- `bench/distill/common/batches.jsonl` 每批追加一行，老师字段写 `deepseek-flash`（next-token.cc 中转，T=0.3，thinking=auto）。

## 5. 规矩

- 直接在 main 上改和提交，不开分支；每批验收完提交一次（题目、`tools/b<批号>/`、老师脚本、batches、exclude、报告）。`local/runs/` 不提交。
- 不碰 `bench/workbank/cases`、`bench/holdout/`、bfcl-product 源码；不改 System、wire、工具 schema。
- 不 ssh 任何服务器。
- 老师自称 DeepSeek 的照收，不筛。
- 拿不准的规格问题停下来问用户，不要当成可优化项自己绕过去。
- 每批结束，用两三句话告诉用户：题数、pass@3、花了多久、有没有要他拍板的事。
