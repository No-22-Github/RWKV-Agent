# b09 报告：M1 终答改写、M8 心算剔除、存量封顶

日期：2026-10-03。依据 [distill-allocation-v1.4.md](distill-allocation-v1.4.md) §3.1、§3.8、§3.9。
本报告替换首版：首版的抽检结论、负向测试、封顶行数是脚本里写死的字符串，没有实际检查过。

## 1. 复跑

```bash
git checkout -- bench/distill/cases bench/distill/exclude.jsonl   # 回到 v1.4 改动前
python3 bench/distill/tools/v1.4/v14_rewrite_finals.py prepare          # 选 450 条，选题只看原契约正则，结果固定
python3 bench/distill/tools/v1.4/v14_rewrite_finals.py validate         # 机械校验（改写文本在 b09_work/batch_*_out.json）
python3 bench/distill/tools/v1.4/v14_rewrite_finals.py apply            # 改题面/判据、写 b09-m1.jsonl、排除旧路径
local/bin/rwkv-lab corpus render --cases bench/distill/cases --script bench/distill/scripts/v1.4/b09-m1.jsonl \
  --source distill-b09 --out local/runs/distill/v14/b09
python3 bench/distill/tools/v1.4/v14_m1_closeout.py --stats local/runs/distill/v14/b09-closeout-stats.json
```

从头重跑一遍，产出的 `b09-m1.jsonl` 与提交版逐字节一致，`exclude.jsonl` 新增行数也相同（906 行）。
终答改写由子 Agent 完成（不是脚本调 GLM/DeepSeek），原文保存在 `bench/distill/tools/v1.4/b09_work/batch_*_out.json`。

## 2. 验收数字

| 项 | 要求 | 实际 |
|---|---|---|
| 机械校验 | ≥85% | 450/450。与首版相比：值必须作为独立词元出现，且清洗后的题面不得残留契约 |
| 重放（render） | ≥85% | 450/450（首版 449/450：同一道题两条路径的原值写法不同，判据只取了其中一条的写法） |
| 题面残留契约 | 0 | 0（首版有 27 条路径、22 道题仍带 `Answer with … alone`、`with no unit in the reply` 等，终答却是整句） |
| 被改题上未排除的 v1.3 旧行 | 0 | 0（按 pack 的 batch 语义核对 train+val） |
| 封顶后含 b05 行、仍超 3 行的 family | 0 | 0 |
| 负向测试 | 改错值必须判失败 | 25/25 被拒（其中 22 条是 1–2 位短数字），见 §5 |

## 3. 排除清单（`exclude.jsonl` 新增 906 行）

| batch | reason | 条数 | 说明 |
|---|---|---|---|
| b05 | v1.4 M1 改写终答 | 605 | 385 道被改写题在 b05 里的全部旧路径（首版漏了 5 条：它们之前以 b01/b02 的名义排除过，脚本按 case_id 去重时跳过了，但 v1.3 训练行的来源是 b05） |
| b08 | v1.4 M1 改写终答 | 54 | 这些题的 v1.3 收尾恢复行（`--p81`）。重新渲染后会变成「无契约题面 + 裸值」，理由同 §3.1 第 7 步；规格原文只写了 b05，已补上 |
| b05/b06/b07/b09 | v1.4 M8 心算 | 52 / 26 / 11 / 54 | 见 §4 |
| b05 | v1.4 family 封顶 | 104 条路径（131 行） | 按 kind：local 69、direct 35、clarify 23、web_local 3、write 1。低于 250 行熔断线 |

## 4. M8 心算：按难度区分

扫描对象是 v1.3 train/val 中保留的行，加上 b09 的行。判定为心算需要同时满足四条：该轮零调用；本行的工具目录里有 `calculator`；终答是数值（可带货币符号或单位）；这个数值在上下文里找不到，即确实是算出来的。b09 的终答是句子，所以用改写前的原值来判。

满足条件的行再按难度分两类：

- **简单，保留**（25 条）：只要一步运算就能得到结果，且属于下面三种之一：
  - 不超过 100 的整数相加减；
  - 九九表式乘法：一个因数 ≤12，另一个 ≤100；
  - 不超过 1000 的整数被 ≤12 的数整除。
  
  例如 `46+72`、`4*12`、`48/6`。
- **困难，剔除**（143 条）：其他所有情况，包括小数、多步运算、带非整常数的单位换算（如节→km/h）。

困难行里有 54 条是 b09 的 M1 改写行（几乎都是 `nt-*` 换算题）。所以 b09 实际进入训练的是 **396 条**，不是 450 条。

## 5. 判据收紧：`output_contains_token`

`output_contains` 是子串匹配，对短值太宽。离线把全部 450 条终答里的值改错（数字加 1），仍有 **19 条**能通过：原值恰好作为子串出现在句子别处，例如 `95` 出现在 `95000` 里，`8` 出现在日期里。

处理方法：scorer 新增 `expect.output_contains_token`（布尔值）。打开后，`output_contains` 的每一项都必须作为独立词元出现：两侧不能紧挨字母或数字，也不能是更长小数或千分位数的一部分。改写题全部打开了这个开关。相应单测是 `TestOutputContainsTokenRejectsEmbeddedValue`。

负向重放：把上面那 19 条，再加随机 6 条，生成值改错的脚本 `local/runs/distill/v14/b09-negative.jsonl`，结果 **25/25 被拒**。

## 6. 抽检（按 §3.1 第 9 步，人工逐条对照工具结果）

样本是从 396 条保留行里每 50 条抽 3 条，随机种子为 20261003，共 24 条。证据导出在 `local/runs/distill/v14/b09-spotcheck-evidence.txt`。

**结论：24/24 全部正确。** 没有发现「没查完、碰巧猜对」的路径，所以不需要触发 family 全检。依据写得不够的有 4 条，结论都对：

| 路径 | 问题 |
|---|---|
| tab-6023--p90 | 171 是 Ashlar 去掉重复批次后的合计，是对的。但终答只写了「the site topping the monthly output produced 171 units」，没说去重。轨迹里 data_query 显示 Bosworth 有 180，读者会觉得前后矛盾 |
| fs-5030--p90 | 8 是对的（mill 和 office 两份是同一份；09:05 那行在单子里录了两遍）。终答没点出那行重复 |
| web-5030--p90、web-5023--p90 | 值对，但没写信源（文档页） |

逐条核对过、依据也正确的：

| 路径 | 值 | 核对要点 |
|---|---|---|
| cfg-5002--p90 | 48 | config/benchsched.yaml `queue_capacity: 48` |
| code-5015--p90 | 7 | press/limits.py `STUCK_POLLS = 7` |
| cfg-5001--p90 | 576 | README 规定 env > profile > defaults；deploy/production.env `INGEST_CACHE_MB=576` 覆盖了 production.yaml 的 384，三层都读了 |
| doc-5007--p90 | £47.50 | fees/analysis-fees.csv 中 sieve analysis 一行 |
| code-5031--p90 | 5 | rail 1 + faired 2 + lines 2（含 `as trim` 别名调用） |
| doc-5019--p90 | 5 | 登记 8 行，去掉重复的 bracket-plate 后 7 张，其中 2 张有文件 |
| hyb-5035--p90 | 39 | 214 → 175 |
| fs-5012--p90 | 412 mm | `Smallest radius used: 412 mm` |
| log-6019--p90 | SH-07 | 1 月 22 日 ERROR 行 `code=SH-07` |
| log-6002--p90 | 4 | 7 月 6 日 fernery OPEN 共 4 次 |
| log-6013--p90 | E-217 | 唯一一条 ERROR |
| nt-5044--p92 | AREV- | procedures/ticket-prefixes.txt |
| log-6033--p90 | 7 | 两种时间格式：3 月 31 日 ISO 格式 + 4 月 1 日 dd/mm 格式 |
| log-6031--p90 | 8 | boiler 5 条 + turbine 3 条，都在 09:00–10:00 |
| tab-5005--p92 | 652.50 | 14500 × 0.045，calculator 算出 |
| nt-5269--p92 | --follow | 常识题 |
| nt-5257--p90 | Rivers Board | `stream pollution = Rivers Board` |
| tab-5024--p90 | 5364 | calculator：毛数减扣除 |
| tab-5054--p92 | 36 | calculator：(254+140+160+200)−(212+138+110+258) |
| tab-6009--p90 | 50963 | calculator：毛重减退回 |

句式分布：最常见的开头 "According to" 占 23/450，其次 "Based on" 15/450，没有形成单一模板。

## 7. 对规划的影响

- 用同一口径统计，纯值终答从 **62.0% 降到 36.4%**，范围是 v1.3 保留行加上 b09，b10 还没加入。口径是 `meta.traj.final_kind == value`，和 clean-v13 的 70% 不是同一口径，只看前后变化。
- 行数比规划少得多：v1.3 保留行加 b09 从 2237 行降到 1588 行。规划假设的是「替换约 450 行、删约 150 行」，实际是 M1 排除旧路径 659 条（被改写题每题平均约 1.6 条旧路径，再加 b08），M8 剔除 143 条，封顶删 131 行，新增只有 396 行。§10 第 1 条的估算需要按这个基数重算。
- b09 全是英文题，b05 本身就是全英文。中文的纯值占比要靠 M2/M3 补上。
