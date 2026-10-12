## Traps
- TR-DECOY: 课程表-上学期.md has last term's class; 「缺交已补」 starts with 缺交 but was handed in later. TR-MULTISRC: six weekly files, README in 作业/说明.md.

## Reference solution
Turn 1: read_file 课程表.md -> 周三第二节 is 线性代数.
Turn 2:
1. bash: `cat 作业/第*.txt | awk '$3=="缺交" {n++} END{print n}'`
Final answers: turn 1 as above; turn 2 states the number printed by the pipeline.

## Why the answer is unique
Turn 1 names its file; turn 2 is an exact-match aggregate over every file the README describes, so one number follows from the fixture.
Why bash is not the tool in turn 1: one named file and one fact, the read tool is the direct read. Turn 2 spans several files, where one pipeline beats opening them one by one.

## Five alternative phrasings of the task
1. 六周里没交作业的记录总共多少条
2. 作业/第*.txt 里状态是缺交的行数
3. 统计缺交（不含缺交已补）的记录总数
4. 这六周一共有多少次缺交
5. How many 缺交 records are there across the six weekly files?
