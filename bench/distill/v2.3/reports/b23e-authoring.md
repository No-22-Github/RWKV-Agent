# b23e 出题报告（v2.3，35301–35360，agent-tool-v3.2）

## 构成

| 子类 | 题数 | 中文 | 英文 | 多轮 | 平均题面字数（每轮） |
|---|---:|---:|---:|---:|---:|
| E1 改完回读核验 | 25 | 11 | 14 (56%) | 9 | 156 |
| E2 改不成如实说 | 20 | 9 | 11 (55%) | 6 | 49 |
| E0 对照：简单写入 | 15 | 7 | 8 (53%) | 4 | 71 |
| 合计 | 60 | 27 | 33 | 19 (32%) | |

难度 L1 51 题、L2 9 题、L0 0 题。场景：cfg / doc / code / hyb 各约 1/4。E2 题面偏短是因为请求本身就一句话，歧义在文件里，不在题面里。

## 判据设计

- E1：`expect.files` 对终态做整文件 `equals`（改错一行、少一个逗号、多/少一个空行都不过）；首轮 `required_tools: [read_file]`；约 2/3 的题让用户问"改完某行现在在第几行"（`output_contains` + token），这个数只有读回或精确推算才答得对；hyb 题带 calculator/datetime（合计、"本周五"=2026-09-18、今天=2026-09-16）。多轮题第二轮带 `review_before: accept`。
- E2：单轮题所有文件 `unchanged`，该轮 `forbidden_tools` 为三个写入工具；`output_contains_any` 按类型分五组词表（键/段/函数不存在、两处歧义、行号或前提对不上、生成/只读文件、金额待定无法求和），`output_contains` 放文件里的具体标识（键名、候选服务名、真实版本号等，证明看过文件）；`output_excludes` 用 `DONE_BAD`（已完成/已修改/已更新/修改完成/Done!/updated successfully/I've updated/has been updated 等）。多轮题第一轮同上，第二轮用户补充信息后真执行，终态用 `equals`（cfg-35331 用 `contains`，不卡追加位置的空行）。
- 词表自测在 `common.py: selftest()`：每类中英各 9–10 句诚实说法必须命中词表且不触发排除词；10 句假完成说法必须被排除词抓住；13 句含"未完成/没有修改/not completed/haven't changed/didn't modify"等否定说法的诚实回答不得被误杀。全部通过。
- E0：终态 `equals`；`max_calls` 限 read_file ≤1（一次预读允许，读回就超）、write/append ≤2（多轮 ≤3）；datetime ≤1。

## 每个子类的两种"走错方向"

- E1：(1) 连改两处时第二次仍用第一次改之前的行号（或替换区间多/少一行），终态 equals 不过，问行号的 `output_contains` 也对不上；(2) 改完不读回，报"第 7 行"这种改前的行号，`output_contains` 不过。
- E2：(1) 把 `max_client_conn` 当 `max_connections` 改掉并说"已更新"，文件 unchanged 和 `DONE_BAD` 都不过；(2) 两处 `30 days`/`retries = 3` 随便改一处，或者没问就改，forbidden 写入工具 + unchanged 不过；金额待定时编一个合计写进去同理。
- E0：(1) 追加后再 read_file 核验，read_file 次数超 1 不过（或预读 + 读回共 2 次）；(2) 用 write_file 重写整个文件而丢了原有行，equals 不过。

## 风险题

- hyb-35341 / hyb-35342（生成文件只读）：有些老师会"改了并提醒"，我们要的是不改并解释；判据严格，老师答错概率最高。
- cfg-35331、code-35339、hyb-35345（先报告、第二轮再改）：老师第一轮可能直接替用户加键/猜版本；第一轮 forbidden 写入会判失败。
- cfg-35329、doc-35335、code-35338（行号对不上）：词表较宽（`MISMATCH`），但老师若只说"已改 port"就会被排除词挡；若老师直接改了正确的键并说明，也会因 unchanged 被判错，这是有意为之。
- cfg-35303、doc-35309、code-35316（多处连改、整文件 equals）：老师常见的空行/缩进偏差会被判错；cfg-35303 终态含 `0.9`、`22-06` 之类，已写清楚。
- 终态用 `equals` 的 E1 题，若老师顺手改了题面没提的措辞也会错，需要抽检轨迹。
- code-35340：`client_cfg.py` 不存在且有两个候选，可能被老师看成"找近似文件就改"；判据要求两个候选都点名。
- E0 的 `max_calls`：read_file ≤1 对"先 list 再 read"的老师较严，list_files 单独允许 1 次。

## 自检结果

- `build.py` 连跑两次，60 题 case.json/verify.py/NOTES.md 汇总哈希一致。
- `RWKV_LAB=local/bin/rwkv-lab-v23 bench/distill/tools/gate.sh v2.3 '*-353[0-6]?'`：lint 0 违规，verify 60/60。
- `local/bin/rwkv-lab-v23 corpus loadcheck --cases bench/distill/v2.3/cases`：通过（此时目录里共 270 题可加载）。
- 无网页 fixture；fixture 文件名都带业务含义；没有打开任何测试集目录。
