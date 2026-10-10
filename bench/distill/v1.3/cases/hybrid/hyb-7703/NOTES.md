## Traps
- TR-DECOY: logs/deploys-2026-09.log mixes ERROR lines from build v2.4.0 (the rollout window)
  with the v2.4.1 lines the request targets. Total ERROR lines are 6; the v2.4.1 subset is 3.

## Reference solution
1. read_file README.md: each line carries a build tag and a service.
2. read_file logs/deploys-2026-09.log. Turn 1: ERROR + build=v2.4.1 lines are 3. Turn 2: two of them (08 and 10 September) sit in the 7-13 September week. Turn 3: the remaining one (19 September) belongs to mail-bridge. Turn 4: WARN + build=v2.4.1 lines are 5.

## Why the answer is unique
Taking all ERROR lines gives 6, but the request names build v2.4.1 and each line names its build, so the three v2.4.0 lines answer a different release. Within v2.4.1 the week boundary is unambiguous (08 and 10 September inside 7-13 September, 19 September outside), so 3, then 2, then mail-bridge, then 5 are the only readings.

## Five alternative phrasings of the task
1. quillon desk september deploy errors by build
2. error lines for build v2.4.1 in september
3. v2.4.1 errors in the week of 7 september
4. which service logged the v2.4.1 error later that month
5. warning count for the september release build
