## Traps
- TR-DUPROW: the export retry wrote exact copies of three of car B's in-window arrivals (11:07:52, 11:31:56, 11:49:47), so the window shows 12 arrival lines for 9 physical arrivals. Counting lines gives 12.

## Reference solution
1. List the workspace: README.md and logs/funicular-journal.log.
2. Read README.md: the export retried, so arrival lines can appear twice.
3. Read logs/funicular-journal.log and count distinct car=B arrival stamps from 11:00:00 up to 12:00:00: 11:04, 11:07, 11:13, 11:22, 11:31, 11:38, 11:44, 11:49, 11:56 = 9.

## Why the answer is unique
Each repeated line is an exact copy of its original including the timestamp, and an arrival is identified by its car and stamp, so the duplicated lines cannot be separate arrivals; the README says the export retried, which is the only event that could have produced them. Counting distinct arrivals in the window leaves 9. The decoy 12 is the raw line count. The answer is 9.
