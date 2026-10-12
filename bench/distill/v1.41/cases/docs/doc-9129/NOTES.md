## Traps
- TR-DECOY: 「延期风险」 lines contain 延期 but are only warnings (周报/README.md); 18 weekly files, one file is not enough.

## Reference solution
Turn 1: read_file 值班/本周.md -> 孙岩 is on duty on Wednesday.
Turn 2:
1. bash: `cat 周报/*.md | grep -c '状态：延期$'`
Final answers: turn 1 as above; turn 2 states the number printed by the pipeline.

## Why the answer is unique
Turn 1 names its file; turn 2 is an exact-match aggregate over every file the README describes, so one number follows from the fixture.
Why bash is not the tool in turn 1: one named file and one fact, read_file is the direct read. Turn 2 spans many files, where one pipeline beats opening them one by one.

## Five alternative phrasings of the task
1. 周报里「延期」状态的项目一共出现几次
2. 所有周报中状态是延期（不含延期风险）的行有多少
3. 统计各周报里延期项目的总条数
4. 18 周周报里延期的项目共多少个
5. How many project lines marked 延期 are in all the weekly reports?
