# b10a（v1.4 M3 第一批：M2 + M3）

产出 265 题（M2 150 行 + M3 115 题 → 165 行），老师为 deepseek-flash（T=0.3，thinking=auto）。
题目 ID 接着 b10 试跑编：cfg-8012 起、doc-8006 起、fs-8004 起、tab-8016 起、log-8010 起、
web-8013 起、hyb-8006 起、code-8004 起、nt-8011 起。

| 文件 | 题类 | ID |
| --- | --- | --- |
| `m2a.py` | M2 诱饵（目标不存在+相近诱饵）cfg/doc | cfg-8012…21、doc-8006…13（18） |
| `m2b.py` | M2 诱饵 fs/log | fs-8004…11、log-8010…17（16） |
| `m2c.py` | M2 诱饵 tab/web/code | tab-8016…27、web-8013…20、code-8004…9（26） |
| `m2d.py` | M2 缺项（键未设/数据缺口） | cfg-8022…31、log-8018…27、tab-8028…33、doc-8014…19、fs-8012…19（40） |
| `m2e.py` | M2 网页失败（fixture 返回 error） | web-8021…35、hyb-8006…20（30） |
| `m2f.py` | M2 部分可答 | tab-8034…41、log-8028…33、doc-8020…22、fs-8020…22（20） |
| `m3a.py` | M3 两轮复述（第 2 轮零调用） | cfg-8032…39、fs-8023…28、log-8034…41、tab-8042…51、doc-8023…30（40） |
| `m3b.py` | M3 单轮禁令 | nt-8011…40、doc-8031…40、cfg-8040…49（50） |
| `m3c.py` | M3 反问点名参数 | tab-8052…57、log-8042…47、cfg-8050…53、fs-8029…32、nt-8041…45（25） |

跑法：`cd bench/distill/tools/b10a && python3 m2a.py`（其余同理；种子固定，重跑逐字节复现）。

`run_check.py` 对 agent-eval run 目录套 b10_check.py 的形态规则 + §3.6 思考统计
（口径照 docs/evaluations/deepseek-teacher-20261010/think_compare.py），冒烟与 S5 复用。

## S5 之后（2026-10-11）

- `common.py`：`revised({id: 理由})` 把判据或题目修过的题升到 version 2，并在 NOTES 写 Changelog（m2a/m2b/m2c/m2d/m2e/m2f/m3a/m3b/m3c 各自登记，共 80 题入库 v2）；`SHELVED` 登记 S5 下架的 12 题，生成后自动移到 `v1.4/cases-shelved/`，所以重跑脚本得到同一套在库题。
- `report_stats.py`：`reports/b10a.md` 里所有数字的复算脚本（读 run 目录、老师脚本、rows、exclude）。
- 老师 run：首轮 `local/runs/distill/v141/b10a/teacher-k0..2`，v2 补跑 `fix-k0..2`；老师脚本由两者各自 `corpus paths` 后按题版本合并（v1 用首轮、v2 用补跑）。
- `exclude_map.py`：把逐条阅读的剔除结论（按「哪一遍 run 产出」记）映射到老师脚本的路径编号，重写 `common/exclude.jsonl` 里 batch=b10a 的行；重抽 paths 后必须重跑。
