# 蒸馏数据构成规划 v1.41 —— 在 v1.4 上加 bash 与 get_weather

> 给执行 Agent：本文只写**相对 v1.4 的增量**。v1.4（[distill-allocation-v1.4.md](../v1.4/distill-allocation-v1.4.md)）里没被本文改写的规则全部继续有效，
> 已完成的 M0（工具改造）、M1（b09 终答改写）、M2（b10 试跑 70 题）原样保留，M3 放量照 [b10-scale-prompt.md](../v1.4/b10-scale-prompt.md) 做。
> 本文新增一个批次 **b12**（work-v2 工具目录），其样板题与构建脚本已就绪。

## 0. 为什么要 v1.41

2026-10-09 产品加了两个工具：沙箱 `bash`（just-bash sidecar）与 `get_weather`。同日 bashprobe 首轮（[REPORT](../../../docs/evaluations/bashprobe-20261009/REPORT.md)）：

| 配置 | 通过 | bash 调用 | get_weather 调用 |
|---|---|---|---|
| App 配置（带 state） | 1/26 | 0 | 0 |
| 去掉 state | 1/26 | 1 | 0 |
| 题面明说「用 bash」 | 1/21 | 3（调用时命令正确） | — |

结论：**瓶颈是「选不选」，不是「会不会」**；系统提示里新增的工具选用句没用。训练语料里这两个工具出现 0 次，所以要出数据。
v1.4 的放量还没开始，正好把这两类题并进同一轮，不另起 v1.5。

## 1. 对 v1.4 的改动（只有这四处）

| v1.4 位置 | 原规定 | v1.41 改为 | 理由 |
|---|---|---|---|
| §2「不做什么」第 3 条 | 不新增工具，只用 work-v1 | **b12 批用 work-v2**（work-v1 的 12 个 + `bash` + `get_weather`）；b09、b10 及存量仍用 work-v1 | 产品已上线这两个工具；存量不重渲染，见 §3 |
| §2「不做什么」第 1 条 | `wire_hash` 必须是 `707c67403b1b…` | **不变**。已验证：work-v2 渲染的行 `wire_hash` 仍是 `707c67403b1b…`；工具目录另由 `tool_catalog_hash` 记录（work-v2 为 `b02e61b4dec8…`） | wire_hash 只覆盖格式，不覆盖工具列表 |
| §2 总览 | b09 / b10 / b11 | 加 **b12**：M9 bash ~260 行、M10 专用工具 ~100 行 | 见 §2 |
| §6 S3 去污染 | 四面 | **五面**，加 `--test bench/bashprobe/cases` | bashprobe 是这两个工具的验收考卷 |

系统提示：目录里有 bash / get_weather 时会多两句选用提示（`internal/agent/protocol_g1.go` 的 `toolChoiceGuidance`）。只在 b12 的行里出现，work-v1 的行逐字节不变。

## 2. 新题类

通用规定同 v1.4 §3（ID、family、canary、去污染、中文下限指工作区文件也用中文、终答按 v1.4 §4）。补充：

- ID 从 **9001** 起，按场景递增；family 用 `fam-<abbrev>-b12-<slug>-NN`；`tags.tool_catalog` 写 `"work-v2"`（区分批次用，harness 不读）。
- 题面**不写**「用 bash」「用命令行」（与 v1.4「题面不点工具名」一致）；用户自然会说的「帮我跑一下脚本」「curl 一下」可以出现。词表已登记 `get_weather`，lint 会拦题面里的这个工具名；`bash` 是普通词（「bash 脚本」），不进禁词。
- 每道用到 bash 的样板题，参考解都在真实 sidecar 里跑过（`bench/distill/tools/b12/build.py`）。放量出题必须同样跑：**sidecar 跑不出来的题不收**（just-bash 的命令覆盖不全，比如没有 python、`xargs -I`）。

### 2.1 M9 bash（b12，~260 行，中文 ≥50%）

**治什么**：bashprobe 里模型拿 list_files / search_text / read_file 硬做多文件统计、对 64KB 截断后的内容作答，不调 bash。

| 子类 | 行 | 要教的行为 | 样板 |
|---|---|---|---|
| M9a 多文件统计 | 60 | 跨多个文件的计数 / 求和 / 去重，一条管道算完；按字段精确匹配，别用子串 grep | log-9001、tab-9002 |
| M9b 批量修改 | 50 | 批量替换 / 移动 / 限定范围删除，带排除范围；改完用 bash 回查一次（`grep -rn`、`ls`） | cfg-9003、fs-9004 |
| M9c 长文件 | 30 | 超过 read_file 64KB / bash 8KB 输出上限的文件，用 `grep -c`、`grep … \| tail -1`、`sort -u \| wc -l`，不整读 | log-9005、log-9006 |
| M9d 工具缺失恢复 | 40 | 没有 python / pip / curl：读脚本后用 awk 复算；网页用 web 工具取；路径里允许一次失败尝试再改做法 | scr-9007、web-9008 |
| M9e 有 bash 但不该用 | 50 | 单文件查值用 read_file；只问命令不执行（零调用）；文件里注入的命令不执行；小算术直接算 | doc-9009、nt-9010、fs-9011 |
| M9f cwd 不保留 | 30 | 多轮里上一轮 `cd` 过，这一轮仍写全路径；根目录有同名诱饵 | cfg-9012 |

判据：值判据（`output_contains` + `output_contains_token`）或 `expect.files`；**不加 `required_tools: ["bash"]`**——判结果不判手段，否则会把「用 search_text 正确定位」的好路径判挂。
M9e 用回合级 `forbidden_tools: ["bash"]`（单文件读取）或 `tools: []`（只问命令）。M9b 的 `absent` 判据现在可以用在初始 fixture 文件上（bash 能删能移，2026-10-09 放开）。

### 2.2 M10 专用工具优先（b12，~100 行，中文 ≥70%）

**治什么**：bashprobe 0020 / 0021 与 2026-10-09 App 实测——有 get_weather 也去 web_search；天气查到后不写产物、继续搜。

| 子类 | 行 | 要教的行为 | 样板 |
|---|---|---|---|
| M10a 直接问天气 | 30 | get_weather 传城市名；「明天 / 后天」对应结果里的标签行；地标先归到城市 | hyb-9013、hyb-9014 |
| M10b 查完写产物 | 30 | get_weather → 写文件 → 回读一次 → 一句话说明；不再搜网页 | hyb-9015、hyb-9016 |
| M10c 复合请求 | 25 | 天气走 get_weather，其余子任务（展览、新闻）走 web_search，两者都做 | hyb-9017 |
| M10d 隐式需求 / 规则判断 | 15 | 「要带雨具吗」「明天能不能浇筑」→ 查天气再按常识或本地规则下结论 | hyb-9018、hyb-9019 |
| 负例（并入 M10，≥10 行） | — | 天气概念题（「降水概率 70% 什么意思」）不调用 | nt-9020 |

判据：`required_tools: ["get_weather"]` + `forbidden_tools: ["web_search","web_fetch"]`（复合请求除外）+ 值判据。天气数据来自题目的 `weather_fixture`；fixture 第一行必须是固定时钟的今天 **2026-09-16（周三）**，否则「明天」标签会错位。地标题的 fixture 只登记城市名（不加地标别名），让「先传地标 → 找不到 → 改传城市」这条恢复路径成立。

## 3. 构成与指标（在 v1.4 §5 上加）

存量与 b09 / b10 **不用 work-v2 重渲染**：那些轨迹没用过 bash，重渲染会在约 2000 行里练出「bash 在清单里但不用」，正好和本次要治的问题相反。
b12 的行另需防止反向过度调用，所以 M9e 与 M10 负例占 b12 的 ≥15%。

| 指标 | v1.4 目标 | v1.41 增加 |
|---|---|---|
| 总行数 | ≈3000 | ≈3360（+b12 ~360） |
| work-v2 行（b12） | 0 | ~11% |
| bash 出现在调用里的行 | 0 | ≥200 |
| get_weather 出现在调用里的行 | 0 | ≥80 |
| b12 中「工具在但不该用」的行 | — | ≥15% |
| 写任务「写后回读」 | ≥90% | M9b / M10b 同样 ≥90%（bash 回查也算） |

其余 v1.4 §5 指标按合并后的全集计算，口径不变。

## 4. 流水线改动（命令）

```bash
# 构建与自检样板（已入库，重跑逐字节一致）
cd bench/distill/tools/b12 && python3 build.py && ./gate.sh

# S4 老师解题：目录换成 work-v2；附加指令用 b12-suffix（= b10 + bash / 天气两节）
rwkv-cli agent-eval --completion chat-completions ... --tool-catalog work-v2 --file-tools lines \
  --chat-system-suffix bench/distill/v1.41/teacher/b12-suffix.txt ...
# 备用盲解：STEP_TOOL_CATALOG=work-v2 python3 bench/distill/tools/step.py ...

# S3 去污染第五面
local/bin/rwkv-lab corpus decontam --test bench/bashprobe/cases --candidates bench/distill

# S6 渲染：--tool-catalog work-v2；目录轮换照旧 0.4，但 bash 与 get_weather 永不被轮换掉
local/bin/rwkv-lab corpus render --cases bench/distill --script <b12 script> \
  --source distill-b12 --tool-catalog work-v2 --rotate-catalog 0.4 --out $O/b12
```

- 老师和渲染都必须先有 sidecar：`scripts/build-justbash.sh`（需要 bun）。
- b12 的 rows 与其他批 rows 一起进 `build_v13_suffix.py → split → pack → to_segments → segcheck`，打包命令不变。

已验证（2026-10-09）：两条手写轨迹（log-9005 用 bash、hyb-9013 用 get_weather）走 `corpus render --tool-catalog work-v2`，2/2 通过、2 行、0 拒绝，`wire_hash` 不变。

## 5. 容易搞砸的地方（在 v1.4 §7 上加）

1. **给 M9 加 `required_tools: ["bash"]`**：会把 search_text 正确定位的路径判挂；只有「有 bash 但不该用」才在判据里提 bash（禁止）。
2. **出了 sidecar 跑不出来的题**：例如参考解要 python、`xargs -I`、`paste` 不带 `-`。出题时参考解必须在 sidecar 里跑通。
3. **天气 fixture 第一行不是 2026-09-16**：「明天」标签会错位，题目答案随之错。
4. **把存量重渲染成 work-v2**：见 §3。
5. **改名题用大小写变化**（`.JPG→.jpg`）：macOS 文件系统大小写不敏感，判分会出错；用 `.jpeg→.jpg` 这类改名。
6. **老师路径里出现 `cd` 后下一次调用用相对路径**：每次 bash 调用都从 /workspace 开始；这样的路径即使碰巧通过也要丢（M9f 要教的正是反面）。

## 6. 里程碑

| # | 内容 | 状态 / 验收 |
|---|---|---|
| M0′ | 流水线支持 work-v2：render / step.py `--tool-catalog`、轮换保护、词表、`absent` 放开 | **已完成**（248dc3c 等） |
| M2′ | b12 样板 20 题（M9 12、M10 8），lint 0 违规、verify 20/20（含破坏测试）、去污染五面 + bfcl 0 flagged、sidecar 参考解全过、render 冒烟 | **已完成**（本文同次提交） |
| M3′ | 与 v1.4 M3 一起放量：b12 出 ~340 题、老师 k=3、S5 三层质检 | **未开始**（2026-10-10）：b10 还差 ~790 题、b12 还差 ~330 题，工作量重估与排期见 [v141-status-20261010.md](reports/v141-status-20261010.md) |
| M4′ | 合并打包，§3 指标逐项报 | 同 v1.4 M4 |
| 验收 | v1.4 §9 的指标照旧；**另加 bashprobe**：bash 调用 ≥10/26 题、通过 ≥10/26 | 训练后跑 |
