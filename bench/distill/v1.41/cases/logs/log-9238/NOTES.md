## Traps
- TR-DECOY: team/RULES.md.bak has the old approval count; [TODO-later] lines start with the same word but are not TODO. TR-MULTISRC: six weekly files, README in notes/README.md.

## Reference solution
Turn 1: read_file team/RULES.md -> merging requires 2 approvals.
Turn 2:
1. bash: `cat notes/week-*.txt | grep -c '^\[TODO\] '`
Final answers: turn 1 as above; turn 2 states the number printed by the pipeline.

## Why the answer is unique
Turn 1 names its file; turn 2 is an exact-match aggregate over every file the README describes, so one number follows from the fixture.
Why bash is not the tool in turn 1: one named file and one fact, the read tool is the direct read. Turn 2 spans several files, where one pipeline beats opening them one by one.

## Five alternative phrasings of the task
1. Count the [TODO] lines over all six notes files.
2. How many open TODO entries do the weekly notes hold in total (parked ones excluded)?
3. Total number of [TODO] tagged lines in notes/week-*.txt?
4. Across weeks 1 to 6, how many items are tagged TODO and not TODO-later?
5. 统计 notes 下各周文件里标记为 [TODO] 的行数
