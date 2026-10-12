## Traps
- TR-MULTISRC: 汇总/2026-08.txt gives only August (69364); the yearly total needs all twelve 明细 files. TR-DECOY: 「华东二区」 shares the prefix with 华东 and must not be counted.

## Reference solution
Turn 1: read_file 汇总/2026-08.txt -> 华东 is 69364.
Turn 2:
1. bash: `cat 明细/*.csv | awk -F, '$1=="华东" {s+=$3} END{print s}'`
Final answers: turn 1 as above; turn 2 states the number printed by the pipeline.

## Why the answer is unique
Turn 1 names its file; turn 2 is an exact-match aggregate over every file the README describes, so one number follows from the fixture.
Why bash is not the tool in turn 1: one named file and one fact, read_file is the direct read. Turn 2 spans many files, where one pipeline beats opening them one by one.

## Five alternative phrasings of the task
1. 华东全年销售额一共多少
2. 把明细里 12 个月的华东销售额加起来
3. 2026 年华东的销售额合计（不含华东二区）
4. 明细表里华东这一年卖了多少钱
5. What is the yearly total for the 华东 region across the monthly detail files?
