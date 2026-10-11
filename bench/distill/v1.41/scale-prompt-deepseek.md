# 给执行 Agent 的提示：v1.41 剩余制作任务（2026-10-11）

> 用法：把下面「---」之间的整段原样交给执行 Agent。它在本机仓库根目录 `/Users/no22/Projects/RWKV-Agent` 工作。
> 凭据在本机 `/Users/no22/.llm_api_key.sh`，提示里只引用这个文件，不含 key 本身。

---

你在 RWKV-Agent 仓库里做 v1.41 蒸馏数据的**放量**：先出新题，再让老师模型在真实 harness 里把题做出来，最后渲染成可训练的行。
当前b10a–e、b11、b13已完成，候选全集3328行。先按现行规划修复样板与旧轨迹，再制作缺失行为；不要重复生成已完成批次。最终包尚未统一后缀与family分割。

本提示是 `bench/distill/v1.4/b10-scale-prompt.md` 的覆盖层。那份文件是基础流程，本提示没提到的地方一律照它执行；两者冲突时以本提示为准。
现行配额与状态以2026-10-11更新的 `distill-allocation-v1.41.md` 为准，覆盖基础提示的旧任务数、进度与比例。老师沿用DeepSeek-flash，保存思考；本阶段交付g1k/state。历史think-full/MiSS双渲染需求单列待实现，不因本阶段剔思考交付而取消。

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

| 剩余任务 | 题目 / 产物位置 | 完成口径 |
|---|---|---|
| P0 发布来源盘点、P1 旧路径替换 | 对已有题重跑时用独立新batch老师脚本，题仍在原版本；报告记录旧路径→新路径映射 | 优先可用替代路径；禁止手删list_files或复制行凑指标 |
| P2 b12 20题样板返修 | `bench/distill/v1.41/cases/`；修改可复现构建源后完整返修重跑 | 零调用禁令、cwd恢复、同文件回查、停止冗余探索、错误恢复抽取 |
| P3 b12a、b12b…新工具增量 | 同上，ID从9021接续并检查冲突；老师和报告在v1.41目录 | 360有效行包含合格样板，bash≥200行、weather≥80行、负例≥60行、多轮≥120行 |
| P4/P5 查询、多轮与零调用修复 | 新补充batch使用 `bench/distill/v1.4/cases/` 和work-v1；报告在v1.41目录，registry明确版本/来源 | 条件预算600查询/多轮行、560首轮零调用行；旧路径替换可减少新增需求 |
| P6 发布包与P7训练验收 | `local/runs/distill/v141/`及版本报告 | 来源隔离、family分割、一次suffix、全集逐项重算；训练后另验收 |

批次名/ID先检查registry与全库占用，不复用b13。每批20–40题完整S1–S8后按有效行重算，达标即停止；不把预算行数当出题数，不为追固定总量制造重复模板。详见规划P0–P7及可复算JSON。

首个返修b12小批须先验证真实目标行为，再放量。原提示“第一批b10a完成后停等确认”的门槛已执行且过时；不重复跑b10a，不因历史停线指令等待批准。真实质量停线（0/3超过25%、接口错误等）仍按共同流程处理。

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
- 闸门：对本批临时cases目录直接运行 `bank lint`（DISTILL canary）与 `bank verify --strict-shape`（含破坏测试），均须通过。gate.sh的lint容错不作通过证据。按现行规格跑六面去污染、全库dedup、hitcheck；bash参考解必须在sidecar跑通。

## 3. 老师解题（S4–S5）

### 3.1 凭据（硬约束）

```bash
source /Users/no22/.llm_api_key.sh     # 导出 API_BASE、API_KEY、MODEL_NAME（deepseek-flash）
```

- 命令行只写 `--api-url "$API_BASE" --model "$MODEL_NAME" --api-key-env API_KEY`。
- **key 不得出现在任何文件、报告、日志、提交、对话输出里**。不要 `echo`、`cat`、`env` 这个文件或变量。
- 端点是 next-token.cc 的中转，同一个 key 下另有 `deepseek-v4-flash`、`deepseek-v4-pro`，**只用 `$MODEL_NAME`**。

### 3.2 二进制

开工时核对当前二进制SHA与协议支持；需要构建时从当前checkout编一次并固定，记录commit和SHA，不切main覆盖已有工作：

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

b10老师配置与suffix已验收，不重复付费冒烟。b12样板行为返修后，在本批20题上k=1，**加suffix和不加suffix各跑一遍**，比较三项（本轮冒烟不能代替之后k=3）：
- pass 数；
- `b10_check.py` 的形态问题数；
- 思考统计（见 §3.6）。

加 suffix 应当不差于不加；明显更差就停下报告用户，不要自己改 suffix 的规则口径。结果写进当前b12返修批报告，记录首轮与重试；统计实际bash/weather、零调用、cwd恢复、同文件回查，不能仅报pass数。

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
- 带思考版渲染（think-full profile）作为独立待办：历史双版本需求保留，本阶段不宣称已实现；待确定空思考监督与profile后单独交付/验收。
- 最终后缀按已有/未加分组处理，只给未加行运行一次 `build_v13_suffix.py`；family与来源隔离后沿用pack/segments/segcheck。不能对混合来源全量再append。
- 报告格式照 `b10-pilot.md`，另加 §3.6 的思考统计、第 0 步冒烟结果、老师 run 目录路径。报告里的每个数字都要能从产物复算。
- `bench/distill/common/batches.jsonl` 每批追加一行，老师字段写 `deepseek-flash`（next-token.cc 中转，T=0.3，thinking=auto）。

## 5. 规矩

- 沿用当前任务分支或 `distill/b<批号>`，保存用户已有改动；每批验收完作聚焦本地提交，不推送（题目、`tools/b<批号>/`、老师脚本、batches、exclude、报告）。`local/runs/` 不提交。
- 不碰 `bench/workbank/cases`、`bench/holdout/`、bfcl-product 源码；不改 System、wire、工具 schema。
- 不 ssh 任何服务器。
- 老师自称 DeepSeek 的照收，不筛。
- 常规制作选择按现行规划推进；只有真实未决范围才说明依据并澄清。配额是实测停止条件，不因预算未出完继续补题。
- 每批结束，用两三句话告诉用户：题数、pass@3、花了多久、有没有要他拍板的事。
