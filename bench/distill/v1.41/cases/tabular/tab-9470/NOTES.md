## Traps
- Turn 1: exact answer 66; the loose reading (站点、类型前缀匹配) gives 145.
- Turn 2: exact answer 60; the loose reading (站点前缀匹配，含地铁口(南)) gives 89.
- TR-MULTISRC: 2 files; the first file alone gives 36.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `cat 单车租借/*.txt | awk '$3=="地铁口" && $4=="电单车" {c++} END{print c+0}'` -> 66
Turn 2: bash: `cat 单车租借/*.txt | awk '$3=="地铁口" && $4=="普通车" {c++} END{print c+0}'` -> 60
Final answer: 地铁口普通车租借共 60 次。

## Why the answer is unique
站点 and 类型 are whole-value columns. The README (单车租借/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 地铁口站点普通车被租了几次？
2. 站点为地铁口、类型为普通车的记录条数。
3. 按说明.md，地铁口（不含南口）的普通车租借次数。
4. 早晚高峰合计，地铁口租出普通车多少次？
5. 统计站点恰好是地铁口且类型是普通车的行数。
