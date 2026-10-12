## Traps
- TR-DECOY: 联系人-旧.txt has an old extension; 「差旅补贴」 shares the prefix with 差旅 and must not be summed. TR-MULTISRC: six monthly files, README in 报销/说明.md.

## Reference solution
Turn 1: read_file 联系人.txt -> 财务主管 分机 8317.
Turn 2:
1. bash: `cat 报销/2026-*.txt | awk '$2=="差旅" {s+=$3} END{print s}'`
Final answers: turn 1 as above; turn 2 states the number printed by the pipeline.

## Why the answer is unique
Turn 1 names its file; turn 2 is an exact-match aggregate over every file the README describes, so one number follows from the fixture.
Why bash is not the tool in turn 1: one named file and one fact, the read tool is the direct read. Turn 2 spans several files, where one pipeline beats opening them one by one.

## Five alternative phrasings of the task
1. 把六个月里差旅类的报销金额加起来
2. 报销/ 下各月文件中 差旅 的合计是多少
3. 4-9 月差旅报销总额（不含差旅补贴）
4. 各月报销文件里类别是差旅的钱一共多少
5. What is the total of the 差旅 category across the monthly files in 报销?
