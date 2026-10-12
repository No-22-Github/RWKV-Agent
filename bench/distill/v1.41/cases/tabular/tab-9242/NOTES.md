## Traps
- Turn 1: exact answer 5833; the loose match (线路包含7路，含17路、27路、7路快) gives 14168.
- Turn 2: exact answer 1834; the loose match (线路、站点都用包含匹配) gives 6638.
- TR-MULTISRC: 4 files; the first file alone gives 278.
- Turn 2 needs a different filter over the same data, so turn 1's number is the wrong answer.

## Reference solution
Turn 1: bash: `cat 班车/*.dat | awk -F';' '$2=="7路" {s+=$4} END{print s}'` -> 5833
Turn 2: bash: `cat 班车/*.dat | awk -F';' '$2=="7路" && $3=="南门" {s+=$4} END{print s}'` -> 1834
Final answer: 7路在南门站上车 1834 人。

## Why the answer is unique
线路 and 站点 are matched as whole values in the semicolon-separated tables. The README (班车/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 7路班车在南门站一共上车多少人？
2. 四周数据里，线路是7路、站点是南门的人数合计是多少？
3. 只算7路和南门站，上车总人数是多少？
4. 按说明.md的口径，7路南门站的上车人数合计。
5. 南门站有多少人乘坐7路上车（四周合计）？
