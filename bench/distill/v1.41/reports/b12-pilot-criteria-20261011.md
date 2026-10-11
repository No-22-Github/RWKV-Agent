# b12 样板判据返修（2026-10-11）

对应 [放量前复核](v141-review-20261011.md) §2 与 [现行规格](../distill-allocation-v1.41.md) P2。本轮只改判据与验收工具，**没有新跑老师**；下表用已有四轮 k=1 冒烟（`local/runs/distill/v141/smoke/b12-{suffix,nosuffix}{,-r2}`）按新判据离线复判。

## 1. 改了什么

| 位置 | 改动 | 解决的问题 |
|---|---|---|
| `nt-9010`、`nt-9020` | 加 `require_active_no_call: true` | `tools: []` 只计入零调用指标、不判失败，`datetime → final` 照样通过并被抽取。现在任何调用都使该轮失败，`corpus paths` 自然剔除。注意 `forbidden_tools` 是精确名单，`["*"]` 不是通配，不能用 |
| `tab-9002`、`scr-9007` | `output_contains` + token 改为 `output_contains_any` + 新增的 `output_contains_any_token`：`7521.21`/`7,521.21`、`2699.2`/`2,699.2`，仍按整词匹配（`17521.21` 不算）；verify.py 同步输出 `expected_contains_any` | 四轮冒烟里 tab-9002 全挂，其中两轮仅因老师写了千分位逗号 |
| `cfg-9012` | 第一轮题面改为「cd 到 服务/结算 目录，看看里面有哪些文件。」；NOTES 参考解改为 `cd 服务/结算 && ls` | 四轮老师全用 list_files/read_file，路径里没有 cd，教不到「cd 不跨调用」 |
| `internal/agent/eval` | 新增 `output_contains_any_token`：把整词匹配用到 `output_contains_any` 的各备选上。单独开关，已同时设 `output_contains_token` 与 `output_contains_any` 的旧题评分不变 | 千分位两种写法都接受，又不让更大的数字混过 |
| `internal/lab/corpus/paths.go` | `get_weather` 的 `location not found` 与 web_fetch 夹具错误页同等对待，不再使整条路径失格；其余 get_weather 错误（参数错）照旧剔除 | M10 地标恢复（鼓浪屿 → 厦门）原本必被 `corpus paths` 丢弃。fixture 决定哪些名字能解析，重放时报同样的错。bash 非零退出本来就是正常 tool_result，不受影响 |
| `tools/b12/behavior.py`（新） | 读 run 目录的 summary + trace，对每条通过路径判 covered / ordinary / reject | 「结果通过」与「目标行为合格」分开计数，见 §2 |

其余 15 道题重建后逐字节不变；`gate.sh v1.41`：lint 0 违规，verify 20/20。

## 2. 行为判据（behavior.py）

- **covered**：通过、无行为问题、且路径上确实有该子类的目标行为。只有它计入 M9/M10 子类配额。
- **ordinary**：通过、无问题，但没有目标行为（如 cfg-9012 没有 bash cd）。可作普通路径保留，不计子类配额。
- **reject**：通过但有行为问题，整路径剔除（按 exclude_lib 的 case/run/k 口径登记）。

通用问题：证据已齐后仍继续调用（答案字面量已出现在结果里、required_tools 已调、规则文件已读；允许紧接着读一次搜索命中的文件或抓一次搜索结果页）、bash 倾倒原始数据（≥4000 字符，或 cat/head/tail/sed -n 无聚合 ≥2000 字符）、输出截断、聚合题用 read_file 整读 csv/log、重复执行缺失命令、终答中途自我更正。

子类目标：M9a/c/e 聚合题须由 bash 结果给出答案且 fs-9011 不得执行注入的 rm；M9b 改动后须有指向目标目录的回查且回查后停止；M9d 须出现真实的命令缺失（exit 127）再换法；M9f 第一轮须 `cd 服务/结算`、第二轮从完整路径访问且不得读根目录诱饵；M10a 地标题首个成功的 get_weather 须是厦门；M10b 写后须回读同文件、之后不再调用、不再泛搜；零调用题不得有任何调用。

## 3. 两轮 suffix 冒烟按新判据复判

| 子类 | 规格行数 | 样板题 | covered / 通过路径 | 样板可计行 | 主要问题 |
|---|---:|---:|---:|---:|---|
| M9a 多文件统计 | 60 | 2 | 0/4 | 0 | 答案已出仍探查（log-9001）；整表倾倒 + paste/bc + calculator（tab-9002） |
| M9b 批量修改 | 50 | 2 | 3/4 | 2 | 一轮回查后又 read_file |
| M9c 长文件 | 30 | 2 | 2/4 | 1 | log-9006 拿到 199 后又跑 3 次 bash |
| M9d 缺失恢复 | 40 | 2 | 2/4 | 1 | scr-9007 从未尝试 python，不构成恢复；且算完又跑 bash |
| M9e 不该用 bash | 50 | 3 | 2/5 | 2 | nt-9010 调 datetime（新判据下失败）；fs-9011 多探查 + 终答自我更正 |
| M9f cwd | 30 | 1 | 0/2 | 0 | 无 cd（题面已改，需重跑验证） |
| M10a 直接天气 | 25 | 2 | 3/3 | 2 | — |
| M10b 天气写产物 | 25 | 2 | 2/2 | 1 | hyb-9016 两轮都因 append 未补换行失败 |
| M10c 复合 | 25 | 1 | 0/2 | 0 | 拿到天气与展览后继续搜索 |
| M10d 隐式/规则 | 15 | 2 | 3/3 | 2 | — |
| M10e 概念负例 | 10 | 1 | 2/2 | 1 | — |

「样板可计行」= 两轮里至少一条 covered 的题数。合计 **12 行**（M9 6、M10 6），其中含 bash 3 行、get_weather 5 行。复核时按 `corpus paths` 保留的是 18 条；新判据下 6 条不再计入配额。四轮全量（含不加 suffix）见 `behavior.py` 直接输出，不加 suffix 的 reject 更多（写后不回读、整读 CSV）。

## 4. 配额重算

v1.4 基线不变：[allocation JSON](v141-allocation-20261011.json) 已按实际保留的 3328 行计算，b12 尚无渲染入库行，`plan.py` 输出不变。变化在 b12 队列内部：

- P3 的 360 行（M9 260 + M10 100）按 **covered 行**计，样板贡献 12 行，剩余 **348 行**（M9 254、M10 94）。bash 调用行剩余 ≥197、天气调用行 ≥75，均以 covered 路径实测，不按题类推算。
- 按两轮样本粗估的单轮 covered 率，k=3 时至少一条 covered 的概率：M9b ≈98%、M9c/M9d ≈88%、M9e ≈70%、M10a/M10d ≈98%、M10b ≈88%、M10e 100%。**M9a、M9f、M10c 为 0**，在它们重跑出 covered 路径前无法估算出题量，不应放量。每类只有 2–6 条路径，这些比例只用于排期，不是预测。

## 5. 下一步

1. 用现行 suffix 对返修后的 20 题重跑 k=1 冒烟（付费，需在本机跑），确认 cfg-9012 出现 cd、nt-9010 不再调用、tab-9002 不因千分位失败；`behavior.py` 输出写进该批报告。
2. M9a / M10c 的「证据够了还继续」在加 suffix 后仍出现。是改 suffix 的停止规则，还是只靠 behavior.py 剔除后多出题，需要你定；scale-prompt 要求不得自行改 suffix 口径。
3. hyb-9016 两轮都因 append 未带结尾换行失败：判据要求整文件相等，属于题面没讲清还是老师错，返修前需确认。
4. 放量批的出题脚本在 `behavior.py` 的 `SPEC` 里登记每题的子类与参数，S5 先跑它，再做 b10_check 与逐条阅读。

复判命令：

```bash
python3 bench/distill/tools/b12/behavior.py local/runs/distill/v141/smoke/b12-suffix-r2 local/runs/distill/v141/smoke/b12-suffix
```
