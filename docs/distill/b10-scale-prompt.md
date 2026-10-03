# 给执行 Agent 的提示：v1.4 M3 —— b10 放量（扩题库 + 产数据）

> 用法：把下面「---」之间的整段原样交给执行 Agent。它会在仓库根目录 `/Users/no22/Projects/RWKV-Agent` 工作。

---

你在 RWKV-Agent 仓库里做 v1.4 蒸馏数据的 M3 里程碑：**b10 放量**。任务分两半：出约 900 道新题，再用老师模型在真实 harness 里把它们做出来，最后得到可训练的行。M2 试跑已经做完，70 道样板题和全部口径都在仓库里。你的工作是**照样板放量，不是重新设计**。

## 0. 先读，按顺序（读完再动手）

1. `docs/distill/distill-allocation-v1.4.md`：§3.2–§3.8 是题类规格，§4 是终答形态，§5 是目标构成，§7 是容易搞砸的地方。这是最高权威。
2. `docs/distill/reports/b10-pilot.md`：试跑报告。**§6「给 M3 放量的口径」是这次最重要的输入**，§5 是试跑里踩过的每一个坑。
3. `docs/distill/distill-workflow.md` §2（出题规则）、§3（S1–S8 命令与闸门）。
4. `docs/distill/b10-solver-brief.md`：终答和路径要长成什么样。老师的输出要按它验收。
5. 样板题：`bench/distill/cases/*/*-80xx`（70 道），以及生成它们的 `bench/distill/tools/b10_build/m2a.py … m8b.py`。fixture 的规模、诱饵的埋法、判据组合、verify.py 怎么写才过得了破坏测试，都照这些来。
6. `docs/workbank/authoring-guide.md`、`docs/workbank/HANDOFF.md` §2、`docs/workbank/M0-findings.md`。

**不得读**：`bench/workbank/cases*`、`bench/holdout/`、`docs/workbank/reports/`、`bench/workbank/reports-data/`、`bench/workbank/ledger/`、`local/runs/` 下的跑分 trace。理由：这些是考卷，读了就会写出考卷的变体，decontam 按表面文本比对查不出来。

## 1. 配额（试跑之外还要的量）

| 题类 | 规格总行数 | 试跑已有（行） | 本次要产出的行 | 中文下限 | 子类配比照 §3 |
|---|---:|---:|---:|---|---|
| M2 查不到 | 150 | 10 | ~140 | 50% | 诱饵 60 / 缺项 40 / 网页失败 30 / 部分可答 20 |
| M3 不调工具 / 反问 | 180 | 17 | ~165 | 70% | 两轮复述 80 / 单轮禁令 50 / 反问点名参数 50（两轮题每轮一行） |
| M4 小清单 | 150 | 10 | ~140 | 40% | 三工具清单 70（一半工作区、一半无需工具）/ read+calc 30 / 五工具+写请求 50 |
| M5 写任务闭环 | 180 | 10 | ~170 | 30% | 保留注释 50 / 多行范围 30 / 依据另一文件 40 / 新建报告 30 / 信息不足不写 30；**要有 script 题**（试跑一道没有），write+script 合计要撑起 §5 的 ≥12% |
| M6 表格 / 日志 | 180 | 10 | ~170 | 30% | 混合日期 40 / 时区 30 / 筛选+连接 50 / 单位混排 30 / 定位行号 30 |
| M7 信源优先级 | 80 | 10 | ~70 | 30% | 官方 vs 二手 40 / 只有二手（官方 error）20 / 预览 vs 正式 20 |
| M8 计算器 | 60 | 10 | ~50 | 50% | 单位换算 / 百分比 / 按天折算 / 多项求和 |

- **ID 接着编**：tab-8016、log-8010、cfg-8012、doc-8006、fs-8004、scr-8001、code-8004、web-8013、hyb-8006、nt-8011 起，各场景各自递增。
- family 用 `fam-<abbrev>-b10-<slug>-NN`，每族 ≤3 题，slug 不与已有 family 重名。canary 以 ` DISTILL-CANARY-<8 hex>` 结尾。`tags.author` 写你自己的模型名，如 `llm:<model>-b10`。
- **分批走完整条线**：每批 120–150 题，批号 `b10a`、`b10b`、`b10c`……每批 S1→S7 全走完再开下一批。第一批先只做 M2+M3，验收过了再放开其他类。

## 2. 出题（S1）硬规则

照 `b10-pilot.md` §6 和样板执行，下面是最容易出错的几条：

1. **判据**
   - 诱饵值进 `output_excludes`；同时必含项要能单独把诱饵答案判挂。不要把「点明诱饵时的解释性提及」也一起排除掉，除非简报明确不许复述（数值、人名不许复述，见简报 §4.7）。
   - 数字考虑英文拼写（3 / three / Three）。
   - 「写不了 / 查不到 / 没核实」词表按真实说法写全，例如「没法创建」「只读」「couldn't」「unchanged」「未经官方」。
   - 长度上限一律 600。
   - 不加与本类无关的硬要求（M8 不要求 web_fetch，M2 不要求特定工具序列）。
   - `required_tools` 里 `read_file / list_files / search_text` 互相等价，`data_query`、`calculator` 不等价。表格题若要求 `read_file`，会把只用 `data_query` 的好路径判挂。
2. **data_query 的真实能力**：只支持等值过滤，没有范围过滤、日期归一和 join。阈值、日期范围题的标准路径是「分组 → 挑组 → 计算器」；连接题是两次查询再加计算器。出题前先用这条路径自己核一遍能不能做。
3. **verify.py 过破坏测试**
   - `bank verify` 会把判分值在 fixture 里的第一个字面量 +1，找不到就删「排序第一的文件」的首行（顺序 .csv < .tsv < .txt < .jsonl < .log < .json < .yaml < .yml < .md，同类按路径排）。
   - verify.py 必须对被改动的那个位置敏感：要么答案值不和无关字面量撞车（日期、时间、编号里的 29、36、07 都撞过），要么校验那一行的格式或内容。
   - 全 `.md` 工作区里 `README.md` 排第一，记得校验它。
4. **CSV 字段含逗号要加引号**（用 csv 模块写），否则 `Mar 11, 2026` 会被拆成两列。
5. **题面不点工具名、不写步骤、不提示陷阱**（lint 查禁词）。查不到类的题面不要直接给出目标路径；工作区要放真正相近的诱饵（同名前缀、旧版本、已停用对象）。
6. 每题的「Why the answer is unique」论证诱饵为什么错，而不是复述正确答案。

每写完一批先自己跑 S2 闸门（lint、单题 verify、hitcheck），再交给主控统一跑全库闸门。

## 3. 产数据（S4–S5）：用 API 让老师真解题

**主路径：`agent-eval --completion chat-completions`，每题 k=3**。参数照 `distill-workflow.md` S4：`--temperature 0.3 --top-p 1 --tool-catalog work-v1 --file-tools lines --max-steps 16 --max-tokens 4096 --decision-max-tokens 8192 --include-draft`，不传 `--profile`。老师端点和模型由用户给（环境变量里的 key，不得写进文件）。只跑本批新题：用 `--case <id>` 逐个传，或把本批题放进临时目录再跑。

**第 0 步（开跑前先决定，并告诉用户）**：现在 `agent-eval` 没有「只给老师看的附加指令」。API 老师只看到 student 的 System，不知道简报里的终答规则（长度、写后回读、不复述诱饵、只用清单里的工具……）。二选一：

- **A（推荐）**：加一个只在 chat-completions 通道生效的 `--chat-system-suffix <file>`，把 `b10-solver-brief.md` §4–§5 压缩成一段附在老师的 system 末尾。
  - 理由：老师的 wire 不进训练数据（`corpus paths` 只带走动作），所以不影响 `wire_hash`。
  - 要求：带测试，证明 `--script` / render 路径的 `wire_hash` 不变；先在 10 道样板题上冒烟，pass@3 与终答形态都要比不加时好。
- **B**：不改代码，靠 S5 过滤。代价是 M5（写后回读）、M7（不复述二手值）、长度这几项的废品率会高，要多出题来补。

**S5 质检，三层都要做，缺一层就会漏**：

1. `corpus paths` 抽路径，按 workflow 做 pass@3 分诊：
   - 0/3 的题逐个重放看失败原因（step.py 和 summary 都只给 PASS/FAIL，要自己读 run 目录的 summary 里每个 case 的 failures）；
   - 判据缺陷 → 改题 version+1、NOTES 写 Changelog，旧路径交给 render 重判；
   - 题目歧义 → 改题重跑；
   - 老师真错 → 下架到 `cases-shelved`。
   - **不得为了通过放宽判据**。一批里 0/3 超过 25% 就停线，先查题。
2. `python3 bench/distill/tools/b10_check.py`（或照它的规则对 paths 产物检查）：写后回读、终答没有 Markdown / 协议文本、不是裸 UNKNOWN、≤600 字、DONE 独占一行、M6 没有整读大表。
3. **逐条读终答**。判分器管不住这四类，试跑 70 条里各抓到 1 条：
   - 凭记忆报会变的外部事实（没有联网工具时报「最新版本是 X」）；
   - 把推测说成事实（替代数据越界）；
   - 同参数重复调用；
   - 取原始行后心算。
   不合格的写进 `bench/distill/exclude.jsonl`，不改脚本、不改 rows。

**备用路径**：API 跑不了的题（比如老师在某类上系统性 0/3，又确认不是题的问题），可以用 `bench/distill/tools/step.py` 让子 Agent 盲解。简报是 `docs/distill/b10-solver-brief.md`；出题者和解题者必须是不同会话；用 `bench/distill/tools/b10_merge.py` 合并。做法见 `b10-pilot.md` §2。

## 4. 渲染与验收（S6–S7）

```bash
local/bin/rwkv-lab corpus render --cases bench/distill/cases --script <本批 script.jsonl> \
  --source distill-$B --rotate-catalog 0.4 --out local/runs/distill/v14/$B/corpus
local/bin/rwkv-lab corpus pack --rows local/runs/distill/v14/$B/corpus/rows.jsonl --exclude bench/distill/exclude.jsonl --max-tokens 8128 --dry-run
python3 bench/distill/tools/build_v13_suffix.py --rows <rows> --out <suffixed>
python3 bench/distill/tools/to_segments.py --rows <suffixed> --out <segments>
local/bin/rwkv-lab corpus segcheck <segments>        # 必须 0 不一致
```

- `wire_hash` 必须是 `707c67403b1b…`。全程不重编 `local/bin/rwkv-cli`（第 0 步 A 改了代码的话，在本批开跑前编好一次，记下 sha256，之后不再动）。
- 闸门：lint 0 违规；verify 全过；decontam 五面都要 0 flagged，命中的题重写或删除，不调阈值：
  ```bash
  local/bin/rwkv-lab corpus decontam --test bench/workbank/cases --candidates bench/distill/cases
  local/bin/rwkv-lab corpus decontam --test bench/workbank/cases-shelved --candidates bench/distill/cases
  local/bin/rwkv-lab corpus decontam --test bench/holdout/p13 --candidates bench/distill/cases
  local/bin/rwkv-lab corpus decontam --test bench/distill/cases-shelved --candidates bench/distill/cases
  local/bin/rwkv-lab corpus decontam --test-suite bfcl-product --candidates bench/distill/cases
  ```
  其中 cases-shelved 那一面上已有 log-5022、log-5024 两条旧命中，与本批无关。
- 每批报告 `docs/distill/reports/$B.md`，格式照 `b10-pilot.md`：
  - 题数（入库 / 下架）、pass@3 分布、0/3 分诊表、paths 丢弃原因计数；
  - render 行数与拒绝原因、抽检剔除清单；
  - 各题类中文占比；
  - §5 构成指标（纯值终答、`data_query` 占比、首动作 `list_files`、零调用、写后回读率）；
  - 每类 3 条终答原文；
  - `wire_hash`、cli sha256、commit。
- **报告里的每个数字都要能从产物复算**，不得手填结论。上一轮有执行模型把抽检结论写死在报告生成代码里，被返工过。
- `bench/distill/batches.jsonl` 每批追加一行（字段照最后一行 b10-pilot）。

## 5. 规矩

- 直接在 main 上改和提交，不开分支；每批验收完提交一次（题目、脚本、batches.jsonl、exclude.jsonl、报告）。`local/runs/` 不提交。
- 不碰 `bench/workbank/cases`、`bench/holdout/p13`、bfcl-product 源码；不改 System、wire、工具 schema（第 0 步 A 的老师通道附加指令除外）。
- 不 ssh 任何服务器；推理和训练机器只走 HTTP 或请用户操作。
- 蒸馏数据里老师自称 Qwen / DeepSeek 的，照收不筛。
- 拿不准的规格问题停下来问用户，不要自己当可优化项绕过去。

## 6. 交付

全部批次做完后，汇总：
- 各题类实际行数与 §1 配额对比；
- v1.4 §5 全表的实际值（把 b09、b10-pilot 与本批合起来算）；
- 未达标项及原因；
- 下架题清单；
- 第 0 步选了 A 还是 B 及冒烟结果；
- 每批报告链接。

---
