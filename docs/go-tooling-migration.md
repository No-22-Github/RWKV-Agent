# 开发工具 Python → Go 迁移 —— 实施规格书

> 给执行迁移的编码 Agent。文中"必须 / 不得 / 不许"是硬约束，每条附理由；其余是建议。
> 核心章节是 **§2 逐文件清单**：哪些迁、迁成什么命令、每个工具的行为要点和基线命令。
> 这是**纯迁移**：输出语义一个字节都不改。发现的 bug 记进 §7，不修。

## 0. 目标

仓库技术栈是 Go，但开发工具里积累了约 9400 行 Python。其中一部分重写了 Go 已有的逻辑
（出题校验、打分、wire 解析），或者手抄了 Go 的内部结构（trace 字段名、工具默认值），
Go 一改它们就静默失效。本次把这部分迁进一个新的 Go 程序 `cmd/rwkv-lab`，删掉已结束实验的
一次性脚本，整理零散的 Go 小命令。

最关键的取舍：**迁移后的每个命令，在同一输入上必须和旧 Python 工具输出相同**（判定口径见 §4.3）。
不追求"顺手改进"——改进放到迁移完成之后单独做，否则无法区分"迁错了"和"故意改了"。

## 1. 总览

范围：git 跟踪的非 Go 代码，排除 `third_party/`、`cmd/rwkv-app/frontend/`（桌面应用界面，本来就是 TS）。

| 档 | 文件数 | 行数 | 处理 |
|---|---|---|---|
| A1 必须迁：重写 Go 已有逻辑 / 手抄 Go 内部 | 20 | 2563 | 迁进 `rwkv-lab` |
| A2 顺带迁：长期在用的出题 / 跑分 / state 工具 | 14 | 2465 | 迁进 `rwkv-lab` |
| B 留 Python：依赖 BFCL 官方 Python 评测 | 6 | 1158 | 不动 |
| C 留 Shell：构建、安装脚本 | 10 | 545 | 不动 |
| D 删除：已结束实验的一次性分析 | 24 | 2709 | 删，留清单 |
| `bench/workbank/cases/**/verify.py` | 155 | — | 不动（是题目数据） |
| Go 零散命令 `cmd/{tokcount,tracecorpus,wirecheck,workreplay}` | 4 | 931 | 两个并入 `rwkv-lab`，两个删 |

**不做什么**（每条都是实现者容易顺手做的）：

- 不改任何算法、阈值、排序规则、输出字段。理由：迁移验收靠"新旧输出一致"，任何改动都会让验收失效。
- 不给 decontam 加中文支持。这是已经规划好的后续任务，要在迁移完成后基于 Go 版本单独做。
- 不迁 B / C / `verify.py`。理由见 §2.4。
- 不改 `internal/agent/eval` 的行为。允许为 `rwkv-lab` 新增**导出**函数（例如单题加载校验），不得改动现有函数的语义。
- 不改历史文档里的路径：`docs/evaluations/**`、`bench/workbank/reports/**`、`bench/workbank/docs/changelog.md`。理由：它们记录的是当时怎么跑的，改了就对不上当时的 commit。
- 不动 `datasets/`、`runs/`、`outputs/`、`state_output/`（都被 gitignore；基线输入会从这里读，但不写回）。
- 不把 `rwkv-lab` 的命令塞进 `rwkv-cli`。理由：`rwkv-cli` 是产品，开发工具单独成一个程序。

## 2. 逐文件清单（核心章节）

下表的"基线命令"是在**迁移起点 commit** 的工作树里运行旧工具的命令（做法见 §6 M0）。
路径 `W=bench/workbank/tools`，`K=.claude/skills/rwkv-bench`，`R=runs/bench-20260923`。

### 2.1 A1：必须迁（20 个文件，2563 行）

| 旧文件 | 行 | 新命令 | 行为要点 / 为什么必须迁 |
|---|---|---|---|
| `scripts/corpus/` 包（11 个模块 + `tests/test_corpus.py`） | 891 | `rwkv-lab corpus paths` / `render` / `decontam` | 见 §2.1.1 |
| `cmd/tracecorpus` | 226 | `rwkv-lab corpus rows` | 已是 Go，搬家并入；逻辑在 `internal/agent/eval/corpus.go`，不动 |
| `$W/lint.py` + `$W/test_lint.py` | 541+188 | `rwkv-lab bank lint` | 出题规则 (a)–(m)，文件头 docstring 有全表。隐藏文件、web fixture 检查与 Go `ValidateCases` 重叠；**两者都保留**，lint 管出题规范，ValidateCases 管 harness 能不能加载，不许合并成一个 |
| `$W/dedup.py` | 122 | `rwkv-lab bank dedup` | 同场景两两比较：prompt 词 3-gram Jaccard > 0.6、fixture 数字集合 Jaccard > 0.5。退出码**恒为 0**（只标记，人来判）——不许改成有命中就返回 1 |
| `$W/wire_metrics.py` + `test_wire_metrics.py` | 214+45 | `rwkv-lab run wire` + Go 函数 `InfrastructureFailure` | 解析 prompt/输出文本（split_think、call_object）。sweep、failure_audit、replicate_summary 都 import 它的 `infrastructure_failure`，Go 版要导出同名函数供其他命令复用 |
| `$K/check_run.py` | 140 | `rwkv-lab run check` | 单次 run 的有效性闸门；`ARMS` 采样档表逐项照搬；失败退出码 1 |
| `$W/capability_gate.py` | 357 | `rwkv-lab run gate` | 分层失败归因（infra → protocol → closeout → …），层的顺序就是判定顺序，不许重排 |
| `$W/failure_audit.py` | 65 | `rwkv-lab run audit` | 机械失败标记，标记可重叠（docstring："not causal buckets"），不许改成互斥分类 |

#### 2.1.1 corpus 包的迁移要点

`scripts/corpus/` 是 2026-09-24 刚从三个旧脚本拆出来的，分层可以直接照搬成 Go 包：

| Python 模块 | Go 位置建议 | 说明 |
|---|---|---|
| `wire.py` | `internal/lab/corpus/wire.go` | 只有 `tool_call(name, arguments)`。**字节必须与 Python 一致**，见 §5 P1–P3 |
| `script.py` | 直接用 `internal/agent/eval/script.go` 的 `ScriptEntry` | 路径编号 `<id>--p<n>` 的两个函数搬过去 |
| `bank.py` | `internal/lab/bank` | 读写题库目录、record → case / 脚本。`TEST_BANK` 守卫照搬 |
| `runs.py` | `internal/lab/runs` | **用 `internal/agent/eval` 的 `TraceRecord`、`agent.Step` 结构体解析**，不许再手写字段名。这是迁移的主要收益之一 |
| `paths.py` | `internal/lab/corpus/paths.go` | `DEFAULTS` 表改为从工具定义取默认值（`internal/agent/tools.go`、`internal/agent/tools/{web,assistant}.go`）；取不到就保留手抄表并加注释说明来源。选路规则：先最短，并列按 run 顺序；之后只收工具序列不同的；每题上限 `--max-per-case` |
| `render.py` | `internal/lab/corpus/render.go` | 仍然用**子进程**调用 `bin/rwkv-cli agent-eval --script`，`BENCH_FLAGS` 逐项照搬。理由：保证和跑分用的是同一套参数解析，wire_hash 才会一致。加载校验改为进程内：逐个题目目录调用 eval 包的加载函数（必要时新增导出函数），**删掉现在"反复调用 agent-eval、用正则解析 stderr"的探测循环** |
| `similarity.py` + `decontam.py` | `internal/lab/similarity` + 命令 | 特征、阈值、5% 模板过滤原样照搬。有命中时退出码 1 |
| `tests/test_corpus.py` | 对应 `_test.go` | 14 个测试全部移植 |

`paths` 终端摘要第一行现在是 `paths: N cases, …`，保持不变。

### 2.2 A2：顺带迁（14 个文件，2465 行）

| 旧文件 | 行 | 新命令 | 行为要点 |
|---|---|---|---|
| `$W/build.py` | 80 | `rwkv-lab bank build` | 按 `tags.status` 过滤、按 id 排序，合并成一个 bank 文件并打印 `bank_version`（sha256）。**输出文件必须与 Python 逐字节相同**——`bank_version` 已写进历次报告，哈希变了就对不上 |
| `$W/coverage.py` | 105 | `rwkv-lab bank coverage` | 场景 × 难度填充表；`--gaps`、`--summary` |
| `$W/calibrate.py` | 113 | `rwkv-lab bank calibrate` | 读 `ledger/cases.jsonl`，对比实测通过率与声明难度 |
| `$W/web_hitcheck.py` | 130 | `rwkv-lab bank hitcheck` | web/hybrid 题的 fixture 能否回答自己 NOTES 里的问题 |
| `$W/verify_all.py` | 413 | `rwkv-lab bank verify` | 把 `files` 物化到临时目录，执行 `python3 -I -S verify.py`（10s 超时、环境只留 PATH/HOME），比对输出与 expect。**Go 版照样调用 python3**：verify.py 本身是题目数据，不迁 |
| `$W/compare.py` | 205 | `rwkv-lab run compare` | 两个 run 目录或两个 ledger 配置名；按题族分组 bootstrap（2000 次，seed 0）。随机数必须复现 Python，见 §5 P7 |
| `$W/ledger.py` | 392 | `rwkv-lab run ledger ingest` / `matrix` | 往 `bench/workbank/ledger/{runs,cases}.jsonl` **追加**，ingest 幂等（已有的 run 行跳过）。新增 `--ledger-dir` 参数（默认仍是原位置），测试和基线都写到临时副本——**不许在测试里写真实 ledger** |
| `$W/replicate_summary.py` + `test_replicate_summary.py` | 88+52 | `rwkv-lab run replicate` | 一组重复 run 的汇总；`--k`、`--out` |
| `$K/sweep.py` | 309 | `rwkv-lab bench sweep` | 采样档 × 套件 × 重复次数的网格；端点快照、每次 run 跑 check、infra 错误整轮重试。凭据只从环境变量 `RWKV_CF_ID` / `RWKV_CF_SECRET` 读，**不许加读文件的途径** |
| `$K/rank.py` | 160 | `rwkv-lab bench rank` | 按预注册规则给采样档排名 |
| `scripts/state-experiment.py` | 135 | `rwkv-lab state run` | 带 canary 与指纹校验的 state 评测驱动（`--state-id --fast --wire --suites --credentials --root --allow-canary-drift`） |
| `scripts/state-corpus-probe.py` | 144 | `rwkv-lab state probe` | 用训练语料前缀做贪心续写，对比有无 state |
| `$W/state_sanity.py` | 139 | `rwkv-lab state sanity` | 直接解析 `.pth`（zip + bf16），三档阈值 ok ≤0.05 / WARN ≤2.0 / FAIL >2.0 或含 NaN/Inf |

说明：sweep、state run、state probe 会访问真实端点，没法拿线上结果做基线，验收方法见 §6 M4（本地假服务器录请求）。

### 2.3 基线命令

每个命令在起点 commit 的工作树 `$BASE` 里跑一次，输出存到 `runs/migration-baseline/<名字>/`；
迁移后用新命令跑同样的输入，按 §4.3 比较。

| 名字 | 旧命令（在 `$BASE` 下执行） |
|---|---|
| paths-148 | `python3 -m scripts.corpus paths --run runs/workbank/relay-dsflash-k0 --run runs/workbank/relay-t03-k0 --run runs/workbank/relay-t03-k1 --out O/script.jsonl --report O/paths.jsonl` |
| paths-40 | 同上，`--run` 换成 `runs/workbank/deepseek-k0` … `deepseek-k3` 四个 |
| paths-cap3 | `--run runs/workbank/postfix-deepseek-k{0,1,2} --max-per-case 3` |
| render-script | `python3 -m scripts.corpus render --allow-test-bank --cases bench/workbank/cases --script <paths-148 的 script.jsonl> --out O` |
| render-records | `python3 -m scripts.corpus render --records <从 700 条 all.jsonl 取前 20 行> --out O` |
| decontam-self | `python3 -m scripts.corpus decontam --test bench/workbank/cases --candidates bench/workbank/cases --report O/r.jsonl` |
| decontam-700 | `python3 -m scripts.corpus decontam --test bench/workbank/cases --records datasets/workspace-agent-700-20260920/generated/normalized/all.jsonl --report O/r.jsonl` |
| lint / dedup / coverage / hitcheck / verify | 各自以 `--cases bench/workbank/cases` 运行（coverage 另跑 `--gaps` 和 `--summary` 各一次） |
| build | `python3 $W/build.py --cases bench/workbank/cases --status all --out O/workbank.json`，再跑一次 `--status reviewed` |
| calibrate | `python3 $W/calibrate.py --ledger bench/workbank/ledger/cases.jsonl` |
| wire | `python3 $W/wire_metrics.py $R/g1k-workbank-greedy-k0 $R/g1k-workbank-t03-p05-k0 --bank <build 基线产出的 workbank.json> --json`（`--bank` 要合并后的单文件，传目录会报错） |
| check | `python3 $K/check_run.py $R/g1k-workbank-greedy-k1 --arm greedy --rwkv`；再对 `$R/g1k-workbank-t03-p05-pr05-k0` 用 `--arm t03-p05-pr05` 跑一次 |
| gate | `python3 $W/capability_gate.py $R/g1k-workbank-greedy-k0 $R/g1k-workbank-greedy-k1 --label greedy --json O/gate.json` |
| audit | `python3 $W/failure_audit.py $R/g1k-workbank-greedy-k0` |
| compare | `python3 $W/compare.py $R/g1k-workbank-greedy-k0 $R/g1k-workbank-t03-p05-k0` |
| ledger | 把 `bench/workbank/ledger` 复制到临时目录，改 `LEDGER_DIR` 指向它，`ingest --config-name base-test --k-index 0 $R/g1k-workbank-greedy-k0`，再 `matrix` |
| replicate | `python3 $W/replicate_summary.py $R/g1k-workbank-t03-p05-k0 $R/g1k-workbank-t03-p05-k1 --k 2 --out O/rep.json`；负向基线：换成 `greedy-k0/k1` 必须报 `missing score or incomplete turns: hyb-0011` 并退出 1，Go 版要同样拒绝 |
| rank | `python3 $K/rank.py runs/bench-20260923 --prefix g1k --save O/rank.json` |
| sweep-dry | `python3 $K/sweep.py --out O/sweep --arms greedy,t03-p05 --suites workbank,bfcl-product --k 0 --dry-run` |
| sanity | `python3 $W/state_sanity.py state_output/sweep_runs/sweep_runs_C/lr3e-4/*.pth` |

以上命令已于 2026-09-24 在当前仓库逐条跑通（lint 0 违规、hitcheck 28 题 0 失败、dedup 无命中）。如果某条命令在起点 commit 上本身就报错（例如某个 run 目录缺文件），换一个同类输入，并在 §7 记一笔。

### 2.4 保留不动（B / C / verify.py）

| 文件 | 为什么不迁 |
|---|---|
| `internal/bfcl/pysidecar/server.py`、`scripts/bfcl.py`、`scripts/bfcl-mt-context-budget.py`、`scripts/bfcl-mt-gt-selftest.py` | import `bfcl_eval`，要执行 BFCL 官方的 Python 函数实现，换不了语言 |
| `scripts/bfcl-mt-archive.py`、`scripts/bfcl-compare-runs.py` | 不依赖 `bfcl_eval`，但产物交给官方 Python 打分器，与上面一组共进退 |
| `scripts/*.sh`（bfcl、build-app、build-macos、build-mlx、build-mlx-ffi、prepare-pth-loader、setup-bfcl、test-macos-native、test-macos-real-model、test-mlx） | 构建和安装脚本，Shell 是合适的语言 |
| `bench/workbank/cases/**/verify.py`（155 个）、`bench/workbank/tools/testdata/**` | 题目数据。出题规范（`bench/workbank/docs/drafting-brief.md` 第 11 条）要求用只依赖标准库的 Python 独立算期望答案；testdata 是 verify_all 的测试夹具，随 `bank verify` 的 Go 测试继续使用 |

### 2.5 D：删除（24 个文件，2709 行）

全部是已出结论的实验分析，不迁移。删除前生成清单 `docs/archive/removed-tools.md`：每行写文件路径、一句话用途（取文件头 docstring 第一句）、删除前最后一次修改它的 commit（`git log -1 --format=%h -- <文件>`），方便以后从 git 历史找回。

| 文件 | 所属实验 |
|---|---|
| `$W/closeout_metrics.py`、`$W/extract_failures.py`、`scripts/closeout-matrix.sh` | 09-17 closeout 归因 |
| `$W/first_step_metrics.py`、`$W/check_user_runs.py` | S1 首步信息源实验、连续 User 块不变量 |
| `$W/evidence_probe_cases.py`、`$W/make_diagnostic_ladder.py`、`$W/run_diagnostic_matrix.py`、`$W/summarize_diagnostic_matrix.py`、`$W/summarize_budget_audit.py` | 09-19~20 诊断阶梯 / 预算审计 |
| `$W/scorer_ablation.py`、`$W/test_scorer_ablation.py` | 09-20 打分器消融。**它在 Python 里重写了一遍打分逻辑**，留着是隐患，所以删而不迁 |
| `$W/state_alignment_audit.py`、`$W/state_case_report.py`、`$W/state_results.py`、`scripts/state-matrix.py` | 09-19 state 对比（state-matrix 把凭据路径和 run 目录写死在代码里） |
| `$W/measure_anchor_agreement.py`、`$W/extract_anchors.py` | 09-21 700 条 anchor 焊接率 / 泄漏清洗（已由 decontam + 来源规则取代） |
| `$W/index_runs.py` | 给 runs 目录生成 INDEX.md，无引用 |
| `$W/reparse.go` | 09-19 离线解析器审计（`go run` 单文件），BFCL 侧已有 `rwkv-cli bfcl-reparse` |
| `scripts/ablation-run-report.py`、`scripts/wire-experiment.py`、`scripts/wire-request-replay.py`、`scripts/bfcl-m2-negative.py` | 09-15 wire 消融、在线 wire 试验、BFCL M2 负样本 |

**删除顺序有依赖**：`state_results`、`summarize_*` import 了 `wire_metrics` / `scorer_ablation` / `failure_audit`，
`sweep.py` 和 `wire-experiment.py` 用 `sys.path.insert` 去 import `wire_metrics`。D 档要和 A 档旧文件在同一个 commit 删，
删完执行 `git grep -n "wire_metrics\|failure_audit\|scorer_ablation\|first_step_metrics"`，只允许在历史文档里出现。

### 2.6 Go 零散命令

| 命令 | 行 | 处理 | 理由 |
|---|---|---|---|
| `cmd/tracecorpus` | 226 | 并入 `rwkv-lab corpus rows`，删目录 | 见 §2.1 |
| `cmd/tokcount` | 54 | 并入 `rwkv-lab tokcount`，删目录 | 数 token 的小工具，无引用但有用 |
| `cmd/workreplay` | 423 | 删除 | 只被 gitignore 的 `datasets/workspace-agent-700-*/tooling/` 旧管线调用，已被 `agent-eval --script` + `corpus rows` 取代 |
| `cmd/wirecheck` | 228 | 删除 | 同上；`corpus rows` 逐步比对回写动作，已覆盖它的检查 |

删 `workreplay` 之前确认 `internal/agent/eval/replay.go` 的导出函数是否还有其他调用方（`git grep -n "eval.Replay\|agenteval.Replay"`）。没有其他调用方就连同 `replay.go` 及其测试一起删；有就只删命令。

### 2.7 要改的文档与引用

只改"怎么用"的文档，历史记录不改（见 §1）：

| 文件 | 改什么 |
|---|---|
| `docs/harness-corpus-render.md` | `python3 -m scripts.corpus …` → `bin/rwkv-lab corpus …`；`cmd/tracecorpus` → `corpus rows` |
| `.claude/skills/rwkv-bench/SKILL.md` | sweep / rank / check_run / compare / ledger / replicate 的命令全部换成 `bin/rwkv-lab …`；第 1 步构建命令加上 `go build -o bin/rwkv-lab ./cmd/rwkv-lab` |
| `INDEX.md` | 工具表里的路径（第 79–82 行附近） |
| `bench/workbank/docs/HANDOFF.md`、`drafting-brief.md`、`authoring-guide.md`、`expansion-152-handoff.md`、`bench/workbank/cases-shelved/README.md` | `uv run tools/xxx.py` / `python3 tools/xxx.py` → 对应 `rwkv-lab bank …` / `run …` |
| `docs/corpus-g1k-wire-format.md` | 引用 `ablation-run-report.py` 处注明已删除，指向 `docs/archive/removed-tools.md` |
| `bench/workbank/cases/{notool/nt-0007,hybrid/hyb-0007}/NOTES.md` | 如果提到工具路径就改；**不许改题目内容本身** |

完成后执行 `git grep -nE "tools/[a-z_]+\.py|scripts/corpus|trace2script|harness_corpus|tracecorpus|workreplay|wirecheck"`，
结果只能落在 §1 列出的历史文档、本文档和 `docs/archive/removed-tools.md` 里。

## 3. 程序结构

```
cmd/rwkv-lab/main.go          只做子命令分发与 --help
internal/lab/corpus/          paths、render、rows（调用 eval.BuildCorpusTurns）、wire
internal/lab/similarity/      decontam 与 bank dedup 共用的特征与打分
internal/lab/bank/            题库读写、lint、build、coverage、calibrate、hitcheck、verify
internal/lab/runs/            读 run 目录（用 eval.TraceRecord / agent.Step）、wire、check、gate、audit、compare、ledger、replicate
internal/lab/bench/           sweep、rank
internal/lab/state/           run、probe、sanity
```

子命令一览（参数名、默认值与旧工具**逐个相同**，只是换了入口）：

```
rwkv-lab corpus  paths | render | rows | decontam
rwkv-lab bank    lint | dedup | build | coverage | calibrate | hitcheck | verify
rwkv-lab run     wire | check | gate | audit | compare | ledger {ingest,matrix} | replicate
rwkv-lab bench   sweep | rank
rwkv-lab state   run | probe | sanity
rwkv-lab tokcount
```

构建：`go build -o bin/rwkv-lab ./cmd/rwkv-lab`。只用标准库和 go.mod 里已有的依赖，不新增第三方包——理由：这些工具只是读写 JSON 和调子进程，不值得为它们引入依赖。

## 4. 接口契约

### 4.1 命令行

- 参数名、位置参数、默认值、`required` 与旧工具相同。旧工具默认路径是相对工具文件所在目录算的（如 lint 的 `DEFAULT_CASES`），Go 版改为相对仓库根目录，并在 `--help` 里写出默认值。
- 退出码相同：lint 有违规 1；decontam 有命中 1；dedup 恒 0；check 闸门失败 1；build / ledger 的参数错误 2。
- 所有写文件的输出**不覆盖已存在的文件**（`O_EXCL`），除非旧工具本来就有 `--force`。理由：旧管线都靠这点防止覆盖上一轮产物。

### 4.2 输出

- stdout / stderr 的分工不变（例如 lint 违规 JSON 走 stdout、汇总走 stderr；sweep 靠 stderr 里的 GATE FAIL 行）。
- 文本输出的每一行和旧工具相同；唯一允许的差异是把程序名写在行首的地方（例如 `paths:`、`tracecorpus:`）。

### 4.3 与基线的比较口径

| 输出类型 | 判定 |
|---|---|
| 文本（stdout/stderr/markdown 表） | 逐字节相同 |
| JSON / JSONL | 逐行解析后深度相等，数字按数值比较（Python 的 `1.0` 与 Go 的 `1` 视为相等），对象的键顺序不要求相同 |
| JSON 里的字符串值 | 逐字节相同。尤其是 `script.jsonl` 里 `outputs[].text` 的 `<tool_call>…</tool_call>`，它会原样进训练语料 |
| `bank build` 产出的 bank 文件 | **整个文件逐字节相同**（见 §2.2，`bank_version` 是它的哈希） |
| `corpus render` 的 `rows.jsonl` | 逐字节相同，且 `run/run.json` 里每题的 `wire_hash` 相同 |

写一个比较脚本或 Go 测试辅助函数实现上表，放在 `internal/lab/labtest`，所有里程碑共用。

## 5. 实现注意事项（这个项目特有的坑）

**JSON 与文本字节**

- **P1** 解析 teacher 的工具参数时不许解码成 `map[string]any`：Go 的 map 序列化会按键名排序，而 Python 保留 teacher 原始的键顺序，`<tool_call>` 文本就变了，训练语料跟着变。用 `json.RawMessage` 或按顺序解析的结构保留键顺序。
- **P2** `json.Marshal` 默认把 `<`、`>`、`&` 转义成 `\u003c` 等，Python `ensure_ascii=False` 不转义。拼 `<tool_call>` 和写 JSONL 时用 `json.Encoder` 并 `SetEscapeHTML(false)`。另外 Go 总是转义 U+2028/U+2029，Python 不转义——遇到就在 §7 记录，不要自己写转义器绕过。
- **P3** `paths` 去默认值时，Python 用 `type(value) is type(default)` 区分 `3` 和 `3.0`：前者去掉，后者保留。Go 默认把两者都解码成 `float64`，必须用 `json.Decoder.UseNumber()` 或 RawMessage 看原始字面量。`tests/test_corpus.py` 里有这条测试（`max_depth: 3.0` 要保留），必须移植。
- **P4** Python `str.splitlines()` 除了 `\n` 还按 `\r`、`\x0b`、`\x0c`、`\x1c`–`\x1e`、`\x85`、` `、` ` 切行；Go `strings.Split(s, "\n")` 不会。decontam 的 fixture 行 3-gram 和 lint 的若干检查依赖这个，要写一个和 `splitlines` 行为相同的函数，并加测试。
- **P5** Python `str.strip()` / `.lower()` 按 Unicode 处理；用 `strings.TrimSpace` / `strings.ToLower` 基本一致，但正则 `\b` 在 Go RE2 里只认 ASCII 单词字符，和 Python 默认的 Unicode 行为不同。decontam 的 `NAME` 正则用了 `\b`——基线（700 条 + 自比）一致即可，不一致就换成显式边界判断，不许改正则的语义。

**排序与计数**

- **P6** `collections.Counter.most_common()` 在票数相同时按**首次出现顺序**排；Python 的 dict 迭代也是插入顺序。Go 的 map 顺序随机，所有"按计数排序"的地方都要用"计数降序 + 首次出现顺序"的稳定排序。paths 的丢弃原因汇总、lint 的汇总都是这种情况。
- **P7** `run compare` 的 bootstrap 用 `random.Random(0)`，结果会写进报告。Go 版必须复现 Python 的随机数：MT19937，种子 0 按 Python 的 `init_by_array([0])` 初始化；`randrange(n)` 等于"取 `k = n 的位数`，反复取 `getrandbits(k)`（32 位以内时就是 `genrand_uint32() >> (32-k)`）直到结果 < n"。先写测试：`random.Random(0)` 前 20 次 `randrange(148)` 的值在 Python 里打印出来，Go 必须逐个相同。**不许换成 `math/rand` 然后说"统计上等价"**——那样历史报告里的置信区间就对不上了。
- **P8** Python `round()` 是银行家舍入（半数取偶），Go `math.Round` 是四舍五入。decontam 的 `round(x, 3)`、以及约 23 处 `round(` / `%.3f` 格式化都要注意；`%.3f` 两边一致，`round()` 要自己实现半数取偶。

**行为边界**

- **P9** `bank verify` 执行 verify.py 时的沙箱条件（临时目录、10s 超时、环境只留 PATH/HOME、`python3 -I -S`）一条都不能少。理由：verify.py 是 LLM 起草的题目附件，这些条件是防止它读到仓库或网络的唯一措施。
- **P10** `run ledger ingest` 是**追加**写入且幂等。不许改成读全部再重写，理由：多个 sweep 可能并发 ingest，重写会丢行。
- **P11** `bench sweep` 的凭据只从环境变量读，写进 run 目录的命令行记录里不许出现凭据（旧版如何脱敏就如何脱敏）。
- **P12** 不许为了让基线对上而加兜底：比如某题输出不同，就在 Go 里对这题特判。遇到解释不了的差异，停下来记进 §7。

**这不是 bug**

- dedup 退出码恒为 0、lint 与 `ValidateCases` 检查有重叠、render 要用子进程调 `rwkv-cli` 而不是进程内跑 eval——都是故意的，理由见 §2。
- `corpus rows` 对多轮题每轮输出一行（`meta.turn`），行数多于题数是正常的：148 题的冒烟里 238 条路径出 242 行。

## 6. 里程碑

### M0 基线（**阻塞项**，约 0.5 天，不需要端点）

不先做基线，后面每一步都没法证明"没迁错"。

1. 起点 commit：引入本文档的那个提交，用 `git log --format=%h --diff-filter=A -- docs/go-tooling-migration.md` 查。它已包含 `scripts/corpus/` 包和 tracecorpus 按轮切行的改动；旧版三个脚本（`scripts/decontam.py` 等）在它之前的提交里，不需要。
2. `git worktree add ../rwkv-migration-base <起点 commit>`，记为 `$BASE`；在 `$BASE` 里 `go build -o bin/rwkv-cli ./cmd/rwkv-cli && go build -o bin/tracecorpus ./cmd/tracecorpus`。
3. 按 §2.3 逐条跑，输出放 `runs/migration-baseline/<名字>/`，同时记下每条命令的退出码、完整命令行。
4. 给 lint / dedup / hitcheck 补**阳性基线**（现有题库全都干净，只有阴性样本不够）：把 `bench/workbank/cases` 复制到临时目录，参照 `test_lint.py` 的做法制造至少 5 种不同规则的违规、2 对近似重复题、1 道 fixture 答不了自己 NOTES 的 web 题，再跑旧工具存基线。
5. 为 P7 存一份 Python 随机数序列：`python3 -c "import random; r=random.Random(0); print([r.randrange(148) for _ in range(20)])"`。

验收：`runs/migration-baseline/` 下每个名字都有输出和退出码；阳性基线里 lint 退出码为 1。

### M1 corpus（约 1 天）

`rwkv-lab corpus paths | render | rows | decontam`，删 `scripts/corpus/`、`cmd/tracecorpus`，改 `docs/harness-corpus-render.md`。

验收：
- paths-148 / paths-40 / paths-cap3、render-script / render-records、decontam-self / decontam-700 七组全部按 §4.3 一致；render 两组的 `wire_hash` 相同。
- `go test ./internal/lab/...` 覆盖原 14 个 Python 测试。
- 负向：把 `wire.go` 的 `SetEscapeHTML(false)` 去掉，paths-148 的比较必须失败（证明比较器真的在比字节）；恢复后通过。
- 负向：`rwkv-lab corpus render --cases bench/workbank/cases …` 不加 `--allow-test-bank` 必须报错，且不创建输出目录。

### M2 出题工具（约 1 天）

`rwkv-lab bank lint | dedup | build | coverage | calibrate | hitcheck | verify`；dedup 复用 `internal/lab/similarity`。

验收：
- §2.3 的阴性基线和 M0 的阳性基线全部一致；`bank build` 产出文件逐字节相同。
- `test_lint.py` 的用例全部移植为 Go 测试；`bank verify` 用 `bench/workbank/tools/testdata` 做测试夹具。
- 负向：往临时副本里某道题的 verify.py 加一行读 `/etc/hosts`（或死循环），`bank verify` 必须报该题失败（沙箱或超时生效），而不是整体挂掉。

### M3 跑分分析 + skill（约 1–1.5 天）

`rwkv-lab run wire | check | gate | audit | compare | ledger | replicate`、`rwkv-lab bench sweep | rank`；改 `SKILL.md`。

验收：
- §2.3 对应各组一致；compare 的置信区间与基线逐位相同（P7）。
- ledger：对临时副本 ingest 同一个 run 两次，第二次不追加任何行（幂等）。
- sweep：`--dry-run` 输出与基线逐字节相同；另外用 M4 的假服务器跑一次非 dry-run 的最小网格（1 档 × 1 套件 × k0），检查写出的 run 目录能被 `rwkv-lab run check` 通过。
- replicate：`greedy-k0/k1` 那组必须和旧工具一样报错退出 1。

### M4 state 工具（约 0.5–1 天）

`rwkv-lab state run | probe | sanity`。

state run / probe 访问真实端点，验收用**本地假服务器**：写一个 Go 测试用的 HTTP 服务器，记录收到的每个请求（方法、路径、请求头去掉凭据后的部分、请求体），返回固定响应。先让旧 Python 工具打到假服务器（把端点地址指过去），存下请求记录作为基线；再让 Go 版打同一个假服务器，请求序列和请求体必须相同。

验收：sanity 在 3 个 `.pth` 上与基线一致；state run / probe 的请求记录一致；负向：把一个 `.pth` 的某个张量改成 NaN，sanity 必须给出 FAIL。

### M5 清理（约 0.5 天）

删 D 档 24 个文件、`cmd/workreplay`、`cmd/wirecheck`（及 §2.6 里确认无调用方的 `replay.go`），`cmd/tokcount` 并入；生成 `docs/archive/removed-tools.md`；改 §2.7 的文档。

验收：
```bash
go build ./cmd/... ./internal/... && go test ./cmd/... ./internal/...
git ls-files '*.py' | grep -v '^third_party/' | grep -v '/verify.py$' | grep -v '^bench/workbank/tools/testdata/'
```
（不要用 `./...`：gitignore 的 `runs/budget-language-audit-20260920/build-overlay/` 里有一份编译不过的旧 Go 代码，会被一起扫到。）第二条命令的输出只能是 §2.4 列出的 6 个 BFCL 文件；§2.5、§2.7 末尾的两条 `git grep` 只能命中历史文档。

每个里程碑单独提交，提交信息写明本步对比了哪些基线、结果如何。

## 7. 已知问题（迁移时不修，只记录）

迁移中发现旧工具的 bug、或 §4.3 口径下解释不了的差异，追加到这里，格式：`工具 | 现象 | 复现输入 | 是否影响历史结论`。已知的：

| 工具 | 现象 |
|---|---|
| `corpus paths` | 原 `runs.py` 检查的重试事件里曾有 `route_retry`，Go 的事件类型里没有这个名字；拆包时已删，对输出无影响 |
| `corpus decontam` | 分词规则 `[a-z0-9]+` 看不到中文，中文题面的 prompt 相似度恒为 0。**本次不修**，迁移完成后单独做中文支持 |
| `bank calibrate` | `--ledger` 被解析但 `collect()` 读的是模块级常量 `ledger/cases.jsonl`，传别的路径不生效，只影响 "no cases in ledger (%s)" 那句话。按 §1「发现的 bug 不修」照搬了这个行为（Go 版同样只把 `--ledger` 用于报错文案）。**要不要修是迁移之后的事**。 |
| `bank verify` | §6 M2 的负向验收写的是「加一行读 `/etc/hosts`」，但新旧两版都**不会**因此失败：`python3 -I -S` 加上只留 `PATH`/`HOME` 并不拦截文件读取，verify.py 照样读到 `/etc/hosts` 并给出正确答案，该题通过。实测新旧报告逐字节相同、都退出 0。真正能触发沙箱的是死循环（10s 超时），那一例新旧一致。 |
| `bank lint` | `verify.py` 的导入检查在 Python 侧走 `ast` + `sys.stdlib_module_names`，Go 侧没有 Python 解析器，改为扫描器（跳过注释与字符串字面量后匹配 `import`/`from` 语句）+ 内嵌 CPython 3.13 的 stdlib 名单。对题库 148 个 verify.py 输出一致；风险是后来新增的 stdlib 模块会被误报为第三方，届时应重新生成名单。 |
| `corpus render` | 旧版有个 `--tracecorpus <bin>` 参数，默认指向 `bin/tracecorpus`；§2.6 把那个程序删了，切行改为进程内调用 `corpus rows`，参数随之去掉。传旧参数的脚本会直接报未知参数，不会静默变行为。 |
| `corpus rows` | 行首程序名由 `tracecorpus:` 改成 `rows:`（§4.2 允许），其余输出不变。 |
| `corpus render` | 加载校验从「反复调 agent-eval、正则解析 stderr」改成进程内调 `eval.LoadCasesDir`（§2.1.1 要求）。判据仍是真实加载器，只是不再起进程；被拒 case 的 reason 文案因此变成 Go 的报错文本。 |
| `run replicate` / `run compare` | 出错时 Python 抛未捕获的 `ValueError`，stderr 是一整段 traceback；Go 版打印 `error: <同样的消息>` 并退出 1。**消息文本一致、退出码一致**，traceback 的外框没法逐字节复刻（§4.3 的文本口径不适用于解释器 traceback）。 |
| `run wire` / `run gate` / `run audit` | `--json` 的报告里，Python 保留 dict 插入顺序，Go 用 map（键按字典序）。§4.3 对 JSON 只要求「逐行解析后深度相等」，所以口径内一致；但如果有人拿这些 JSON 做逐字节 diff，会看到键序不同。需要逐字节的话，把报告改成 `lab.OrderedMap` 即可。 |
| `bench sweep` | 凭据只从 `RWKV_CF_ID` / `RWKV_CF_SECRET` 读（P11）；`experiment.json` 里记的是 `--api-header-env CF-Access-Client-Id=RWKV_CF_ID`，即变量名而非值。`--dry-run` 输出里的二进制路径由仓库根推导，从别的 worktree 跑基线时路径不同（实测只有这一处差异）。 |

## 8. 交付与验收

完成后交回的东西：
1. M1–M5 的提交列表；
2. 一张表：§2.3 每个基线名字 → 新命令 → 比较结果（一致 / 不一致及原因）；
3. §7 的追加内容；
4. `git ls-files` 前后对比：删了哪些、加了哪些。

验收方会抽查：重跑 M1 的 paths-148 与 render-script、M3 的 compare、M5 的两条清理命令，并检查 §5 的 P1、P3、P7 各有对应测试。
