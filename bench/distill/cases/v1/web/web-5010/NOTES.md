## Traps
- TR-EARLYHIT: the first result, docs.windrow.example/reference/limits, already states the standard-plan rate, so one search is enough; docs.windrow.example/reference/trial-limits is a second page whose 3-per-second ceiling belongs to trial workspaces and is the decoy.

## Reference solution
1. Search once for the Windrow sending limits: the first result is the standard-plan page, whose snippet gives 14 messages per second, and the trial page is listed with it.
2. Open docs.windrow.example/reference/limits and confirm the standard-plan rate of 14 messages per second; answer 14.

## Why the answer is unique
The two pages describe different plan types and the question names a standard plan. The standard-plan page states 14 messages per second; the trial page states 3 per second and says that moving to a paid plan lifts its ceilings, so 3 is a trial ceiling, not the standard-plan rate. 250000 is a daily ceiling and 1 second is the retry delay after a 429, neither of which is a per-second send rate.

## Five alternative phrasings of the task
Every query below carries the fixture keyword windrow, so each one is answered by a fixture entry.
1. windrow sending limits standard plan
2. windrow messages per second reference
3. windrow standard plan rate limit
4. windrow how many messages per second
5. windrow email sending rate reference
