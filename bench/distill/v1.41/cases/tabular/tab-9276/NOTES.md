## Traps
- TR-READONLY: 库存/模板.txt keeps its units. TR-DECOY: 「件套」 starts with 件 (a substring `s/件/个/` also rewrites it). The turn-2 count includes rows that were 个 before turn 1.
- Turn 2 asks about the whole tree, including files that already differed before turn 1.

## Reference solution
Turn 1:
1. bash: `find 库存 -name '2026-*.txt' | xargs sed -i 's/,件$/,个/'`
2. bash: `grep -c ',个$' 库存/2026-07.txt 库存/2026-08.txt 库存/2026-09.txt`
Final answer: DONE (三个月的「件」已改为「个」).
Turn 2:
1. bash: `cat 库存/2026-*.txt | grep -c ',个$'`
Final answer: 22 行.

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.

## Five alternative phrasings of the task
1. 三个月合计，单位为个的有几行？
2. 统计 2026-07 到 2026-09 里单位列是「个」的行数
3. 改完以后「个」一共多少条记录（不含模板）？
4. 库存里单位等于个的记录总数是多少？
5. How many rows have the unit 个 in the three monthly files now?
