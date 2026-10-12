## Traps
- TR-DECOY: exact answer 人民广场(东); the loose reading (方向前缀匹配，含出站(换乘)) gives 火车站.
- TR-MULTISRC: 5 files; the first file alone gives 人民广场.

## Reference solution
Turn 1: bash: `cat 地铁客流/*.txt | awk -F';' '$3=="出站" {s[$2]+=$4} END{for (k in s) print s[k], k}' | sort -rn | head -1` -> 人民广场(东)
        the same pipeline prints the total (9605) next to the name
Final answer: 出站人数合计最多的是人民广场(东)，合计 9605 人。

## Why the answer is unique
站名 and 方向 are whole-value columns of the semicolon-separated tables. The README (地铁客流/说明.md) fixes the rule; the answer is a single name.

## Five alternative phrasings of the task
1. 五天里出站客流最大的站是哪个？
2. 按说明.md，出站人数加起来最高的站名是什么？
3. 哪个站的出站人数总和排第一（换乘不算）？
4. 统计方向列恰好是出站的人数，按站名汇总后最多的是谁？
5. 周一到周五，出站旅客最多的站点。
