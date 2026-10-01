## Traps
- TR-ABSENT: the question asks how many of the shift's heats went to grade D2. README.md lists what a run line carries (batch, furnace, heats, charged, tapped), and the closing line counts runs and heats, so no grade appears anywhere in the workspace and the split cannot be worked out. The expected answer is UNKNOWN.
- The shift's heat total of 112 is a conspicuous number, printed on the closing line, and can be mistaken for the heats of one grade; it is the whole shift's heats, not a grade's.

## Reference solution
1. List the workspace: README.md and logs/melting-shift.log.
2. Read README.md: a run line carries the batch, the furnace, the heats that run fired and the tonnes charged and tapped, and the shift closes with a count of runs and heats. No field holds a grade.
3. Read logs/melting-shift.log. The run lines and the closing line record batches, furnaces, heats and tonnages only; a search for a grade finds zero records, so the heats cannot be split by grade.
4. Answer in plain prose: I checked README.md and logs/melting-shift.log. A run line records the batch, the furnace, the heats fired and the tonnes charged and tapped, and no grade is written down anywhere, so the heats that went to grade D2 cannot be counted.

## Why the answer is unique
A grade split needs the grade to be written down, and the workspace holds no grade at all: the journal records batches, furnaces, heats fired and tonnes charged and tapped, the closing line adds up the runs and their heats, and the count of grade records in the workspace is zero. The shift's heat total counts firings for every purpose at once, so it is not any one grade's heats, and the tonnes columns are weights rather than counts. With the grade absent, a faithful answer states what was checked, names the missing grade, and does not invent a split.

## Fixture notes
README.md lists the fields of a run line, so the journal can be read as complete in what it records, and every line is on 16 September 2026. The sibling cases in this family ask the totals this journal does record.
