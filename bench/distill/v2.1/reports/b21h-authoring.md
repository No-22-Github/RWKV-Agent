# b21h 出题报告（v2.1，题号 32301–32350，共 50 题）

主题：拿到空结果 / 0 / 报错时，先看样本行、表头或文件列表找原因，修正后再算；命令不存在就换可用命令。生成脚本 `bench/distill/tools/b21h/`。

## 构成
- 子类：格式不一致 12（32301–32312）、列位置/分隔符 10（32313–32322）、文件选错 8（32323–32330）、用词不同 8（32331–32338）、命令不可用/报错 12（32339–32350）。
- 场景：tabular 25、logs 14、config 11（未用 hybrid，避免 web 题的"五种问法"要求）。
- 中文 31（62%）/ 英文 19；多轮（2 个用户轮）17（34%）；难度 L1 18 / L2 32（多轮、文件选错、命令不可用类 ref_calls 记 5 → L2；其余 L1）。
- tool_policy：全部 `must_offer: [bash, read_file]`；其中 15 题（30%）另加 `never_offer: [calculator, data_query]`，其余不限制。
- 答案形式：数字 ≥ 2 位（无千分位写法风险，总和均 < 1000）、人名/代号/关键词；凡 output_contains 里没有汉字的轮次（66 轮）都开 `output_contains_token`（Han 字符算边界，"共 20 条"能匹配，日期里的 "2026" 不会蒙中 "20"）；含汉字名的轮次不需要。已无未加 token 的 1–3 位裸数字判据。

## 数据量（返修后）
计数/统计类 fixture 150–330 行（日志 300 行上下，表格 150–260 行，中位数题 301 个值）；配置类 65–125 行，其中开关题 64 个条目，其余配置文件含 80 行左右的无关键值作噪声（噪声键名避开目标关键词，保证顺手命令仍得空/0）。数值总和一律 < 1000，避免千分位写法。答案随数据重算，参考命令与顺手命令在沙箱重新实测通过。

## 判据设计
- `output_contains` 放修正后的正确值；多轮每轮各自的值。
- `output_excludes` 只放"顺手命令"得到的数字结论（"共 0""为 0""is 0"" 0 orders"等，开头带汉字或空格以免误伤 "10 条"）。**刻意不放"没找到/没有 X/not found/cannot"类否定短语**：诚实回答"按 X 搜不到，改用 Y 找到 N"会命中它们（b20abc 返修的教训）。因此命令不可用类、取值类题（文件选错的 err 型、查字段值）没有 excludes，只靠答案正确性。无 excludes 的轮次约 37 个。
- verify.py 校验 fixture 的 sha256 后由 fixture 重算答案（首轮答案）；`bank verify --strict-shape` 含 sabotage 全过。

## 沙箱实测（build.py 的 `run_checks`，每次构建都真跑）
- 参考命令 ≥ 62 条，输出必须含正确答案；"顺手命令" 69 条，断言：zero=输出恰为 0（如 `grep -c refunded`、`awk -F, … sum`、`awk -F, '$2==…'` 在 TSV/分号/管道文件上）、empty=输出为空（`grep timeout_seconds`、`grep -E '^42,'`、awk `asort` 静默输出空行）、err=退出码非 0。
- 实测要点：python3/perl/sqlite3/csvstat/mlr 均 exit 127；`awk strftime()` 报 "not implemented" exit 2；jq `fromdateiso8601` 报 Unknown function；awk 读不存在文件 exit 2；`awk -F'|'` 会把 `|` 当正则报 "start index out of bounds"，参考解用 `-F'[|]'`；CRLF 下 `$NF=="failed"` 和 `,failed$` 均为 0（数值型末列如 `$3=="10"` 在此 awk 里反而会匹配，所以 CRLF 题的末列用文字值）；`date -d @epoch +%F`、`date -d 2026-09-15` 可用。

## 自检
- build.py 连跑两次 150 个文件逐字节一致。
- `gate.sh v2.1 '*-323[0-5]?'`：lint 0 违规，verify 50/50。
- `corpus loadcheck`：514 题全部加载通过（含其他批次，无报错）。

## 已知风险
- 老师若一上来就读文件头再写对命令，会直接通过：判据只看终答，不能保证"先踩坑再修正"，但每题第一条顺手命令确实得 0/空/错，且是可选的。
- 题面里"用 python/perl/mlr"等诱导词在老师那里可能直接被改写成 awk 而不先试；不影响通过但减少"报错后换命令"的样本，可在轨迹层面筛。
- 无 excludes 的轮次（约 37）若老师编造答案只靠 contains 判，数值题撞数概率低但非零。
- fixture 均为程序生成（固定种子），主题词有重复（订单/日志），去污染检查若撞题请直接删。
- L3 未用。

## 老师最可能答错的 5 题
1. tab-32345：epoch 转日期，沙箱 awk 无 strftime，需改用 `date -d @`，且两轮日期都要对。
2. tab-32350：`asort` 静默输出空行（不报错），容易把空值当答案或编造中位数；41 个值需取第 21 个。
3. log-32334：超时有 ETIMEDOUT 和 deadline exceeded 两种写法，容易只数一种。
4. tab-32338：周末订单要由日期推算星期，需循环调用 `date -d`。
5. cfg-32330：port 在被 include 的 local.ini，pool 被覆盖成 30（settings.ini 里是 12）。
