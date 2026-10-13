## Traps
- Answer: 9158. TR-DECOY: including 东1临时 gives 17096.
- Data volume: 1 data files, 130 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `grep ' 入口=东1 ' 停车场/进出记录.log | grep ' 月卡=否$' | awk '{split($5, a, "="); s+=a[2]} END {print s}'` -> 9158
Final answer: 东1入口临停车共收费 9158 元（东1临时不算）。

## Why the answer is unique
入口、月卡是精确字段；记录按出场顺序追加。
