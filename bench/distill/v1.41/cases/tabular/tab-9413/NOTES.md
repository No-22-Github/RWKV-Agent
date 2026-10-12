## Traps
- TR-DECOY: exact answer 86; the loose reading (棚号前缀匹配，含3号(东)) gives 99.
- TR-MULTISRC: 2 files; the first file alone gives 84.

## Reference solution
Turn 1: bash: `cat 大棚监测/*.dat | awk -F, '$2=="3号" && $3=="上层" {print $4}' | sort -rn | head -1` -> 86
Final answer: 86%。

## Why the answer is unique
棚号 and 位置 are whole-value columns. The README (大棚监测/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 3号棚上层的湿度峰值是多少？
2. 棚号为3号、位置为上层的最大湿度值。
3. 按说明.md，3号上层最高湿度百分比。
4. 两个区里3号棚上层记录到的最高湿度。
5. 3号棚（不含3号(东)）上层的湿度最大值。
