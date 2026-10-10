## Traps
- TR-MISSING: four rows carry dur=NA (pipeline glitch per the README), so they have no duration at all; two more rows are exactly dur=5.00s. Treating the NA rows as long queries or counting the remaining 5.00s row as "over 5" both inflate the total; the naive count is the recorded decoy 13, the strict count is 12.

## Reference solution
1. Turn 1: read README.md (dur=NA rows have unknown duration; 5.00s is exact), read logs/db-slowquery.log, count rows with numeric dur > 5s: 5.6, 6.8, 6.3, 8.4, 7.9, 5.9, 5.2, 6.1, 7.0, 8.8, 9.1, 9.4 = 12. Answer: 12 条.
2. Turn 2: within [00:00:00, 03:00:00): 5.6, 6.8, 6.3, 8.4, 7.9, 5.9 = 6. Answer: 6 条.
3. Turn 3: drop the two etl_batch rows (8.4 at 01:40:08, 5.9 at 02:30:44): 4. Answer: 4 条.
4. Turn 4: the slowest survivor is 7.9 (02:05:26). Answer: 7.9.

## Why the answer is unique
The README pins the semantics of both irregular values: dur=NA has no number behind it and cannot be compared, and 5.00s is exactly 5, which "超过 5 秒" excludes, so the count is fixed at 12 (the single remaining dur=5.00s row sits exactly on the boundary). The morning window and the user exclusion each carve a subset of that list deterministically, and 7.9 is the maximum of the four survivors.
