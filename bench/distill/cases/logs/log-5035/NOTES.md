## Traps
- TR-ABSENT: the question asks how many of the shift's heats went to grade D2. README.md lists what a run line carries (batch, furnace, heats, charged, tapped), and the closing line counts runs and heats, so no grade appears anywhere in the workspace and the split cannot be worked out. The expected answer is UNKNOWN.
- The shift's heat total of 112 is a conspicuous number, printed on the closing line, and can be mistaken for the heats of one grade; it is the whole shift's heats, not a grade's.

## Reference solution
1. List the workspace: README.md and logs/melting-shift.log.
2. Read README.md: a run line carries the batch, the furnace, the heats that run fired and the tonnes charged and tapped, and the shift closes with a count of runs and heats. No field holds a grade.
3. Read logs/melting-shift.log. Eighteen runs and the closing line report 112 heats for the shift, and nothing anywhere in the workspace splits them by grade.

## Why the answer is unique
A grade split needs the grade to be written down, and the workspace holds no grade at all: the journal records batches, furnaces, heats fired and tonnes charged and tapped, and the closing line adds up the runs and their heats. The decoy 112 is the shift's total heats, which says how many times the furnaces fired rather than how many of those firings were for one grade, and the tonnes columns are weights rather than counts. Since the data needed to answer is absent, the only sound reply is UNKNOWN.

## Fixture notes
README.md lists the fields of a run line, so the journal can be read as complete in what it records, and every line is on 16 September 2026. The sibling cases in this family ask the totals this journal does record.
