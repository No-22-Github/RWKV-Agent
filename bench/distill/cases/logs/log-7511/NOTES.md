## Traps
- TR-HEADER: the [report] summary row reads 失败 12 次 as of 23:00; treating it as the day's total gives the decoy 12. One more build fails at 23:58:44, after the report job's cut-off (README), so the row count for the day is 13.

## Reference solution
1. Turn 1: read README.md (the [report] line only covers 23:00 and earlier), read logs/ci-builds.log, count result=failed rows: 12 before 23:00 plus BR-3331 at 23:58:44 = 13. Answer: 13 次.
2. Turn 2: sim-tests failures: 09:12:44, 10:15:38, 11:31:07, 13:05:12, 14:29:51, 16:47:20, 22:58:44 = 7. Answer: 7 次.
3. Turn 3: the earliest of those is BR-3287 (09:12:44). Answer: BR-3287.
4. Turn 4: ci-04 failures: 10:15:38, 14:29:51, 19:08:42 = 3; 13 - 3 = 10. Answer: 10 次.

## Why the answer is unique
The summary row is stale by construction: the README pins its cut-off at 23:00 and BR-3331 fails at 23:58:44, so the summary's 12 and the row count 13 are both correct for their own scopes and only one answers the question. Every build row carries exactly one stage and one worker, so the sim-tests subset (7), the first failing build id and the ci-04 exclusion (13 - 3 = 10) each have a single reading.
