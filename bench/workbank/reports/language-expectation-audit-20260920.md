# Substring 判据的语言耦合审计（2026-09-20）

扫描当前仓库实际解析后的 smoke 10、boundary 18、assistant 6、BFCL product 60、Workbank 40，共 134 题。`expectationaudit` 导出每个 turn 的 `OutputContains` / `OutputContainsAny`，共 126 个判据值；完整题号、prompt、字段和值及逐项处理建议见同名 JSON。未改任何正式判据，未用此扫描重新计算官方分数。

动态生成的 BFCL `toolHint`、`multi.Value` 已被解析，避免只扫源码字符串而漏报。另查了 native eval 的 Go/JSON 定义：primitive 生成器还有数字 `1887357`，没有新增自然语言候选。未将测试夹具、任意外部导入题库或历史冻结快照冒充当前五套 native suite；本审计不覆盖 `OutputEquals`、`OutputExcludes` 等其他判据的全部语义。

## 逐组处理决定

| 候选组 | 题数 / 值数 | 具体值 | 审计建议 |
|---|---:|---|---|
| BFCL 缺参澄清 | 10 / 10 | `路径` ×5、`关键词` ×5 | 将“确实询问缺失的参数”与“回复语言”分列。先用同轨迹人工/语义诊断，未来版本可接受英文 path/keyword 等语义等价表述；不能只出现单词就认定发生澄清。 |
| BFCL 错误恢复第一轮 | 10 / 10 | `不存在`，另有 fixture value 的 OR 分支 | 将“如实报告缺失／有效恢复”与语言分列。题面写“没有找到”，判据写“不存在”，连中文同义表述也会失配。保留第二轮工具及参数约束。 |
| assistant 缺参澄清 | 1 / 1 | `城市` | 与 BFCL 缺参同样处理；询问地点不一定必须出现“城市”二字。 |
| assistant 汇率不可用 | 1 / 1 | `不可用` | 单列“承认无法换算且不编造汇率”，再看语言遵循。不能把 `unavailable` 的等价表达自动当内容错误。 |
| assistant 天气事实 | 3 / 3 | `多云` | 天气条件的语义归一化与语言分开，继续检查温度等事实。这是本地化事实，不只是格式。 |
| Workbank `nt-0003` | 1 / 17 | cannot / Cannot / can't / Can't / can’t / unable / Unable / no tool / No tool / don't have / Don't have / not able / Not able / not available / Not available / not possible / Not possible | 判为英文拒绝短语耦合。未来诊断应检查无法执行邮件请求的事实及拒绝含义，不能随意加入泛化 `not`；保留原有 UNKNOWN 分支并单独报告其命中。 |
| Workbank `code-0002` | 1 / 2 | `1 failed`、`1 skipped` | **不属于隐式耦合**：题面明确指定 `'<N> failed, <M> skipped'`。官方契约继续精确，另外拆出两项计数正确性。 |
| assistant 地铁站名 | 1 / 1 | `世纪大道站` | 实体身份检查，默认保留；如支持跨语言答案，仅接纳经确认的实体别名。不能机械当作泛用自然语言放宽。 |
| assistant 日期 | 1 / 1 | `2026年8月4日` | 已有 `2026-08-04` 同一 OR 分支，不需立即处理。 |

前六组共 **26 道不同题、42 个判据值**：39 个隐式短语耦合值、3 个本地化天气事实值。后面有重叠题号，不应再简单相加计算总题数。另 80 个值归为数字、代码标识符、文件路径或显式固定回执；如 `APPROVED`、`EMPTY`、`UNKNOWN`、`MISSING-CONFIRMED` 虽然像英文词，但在题目里是 fixture 值或契约标记，保留精确检查。

## 已有在线证据与静态候选分开

此前 BFCL fast 缺参子集的 9 个失分轨迹都是英文澄清、没有工具执行，支持这 9 题存在实际评分失配；其余候选由本轮静态扫描发现，不代表已经证实发生了相同误判，更不能从 26 个候选题推算涨分。

后续若建立双语或语义判据，须冻结成独立版本/诊断臂，用同一批输出配对计算；既不静默改历史成绩，也不把这份候选表当作新 scorer。

## 复现

```sh
go run ./bench/workbank/tools/expectationaudit bench/workbank/cases \
  > runs/budget-language-audit-20260920/expectations.json
```

同名 JSON 是本次导出后的人工归类快照，包含全部 126 条及逐条建议。重新导出不自动复制这次人工语义判断。
