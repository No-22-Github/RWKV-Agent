## Traps
- TR-READONLY: hold-*.txt stay in incoming. TR-MULTISRC: done/ already held five older files, so the turn-2 total covers 13 files, not just the eight moved ones.
- Turn 2 asks about the whole tree, including files that already differed before turn 1.

## Reference solution
Turn 1:
1. bash: `mv incoming/report-*.txt done/`
2. bash: `ls incoming done`
Final answer: DONE (eight report files are in done, hold files stay in incoming).
Turn 2:
1. bash: `cat done/* | wc -l`
Final answer: 99 lines.

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.

## Five alternative phrasings of the task
1. Total line count across everything in done after the move?
2. How many lines are there in done in all?
3. Sum the lines of every file now in the done folder.
4. What is the combined number of lines of the files in done?
5. 现在 done 目录里所有文件一共有多少行？
