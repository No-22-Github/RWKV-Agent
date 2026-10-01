## Traps
- TR-MISSING: two failed builds carry duration_s null (killed before completing, README). Treating null as a huge runtime inflates the long-build count to the recorded decoy 6; only measured durations compare, so 4 builds ran longer than 900 seconds.

## Reference solution
1. Turn 1: read logs/build-events.jsonl, count event=failed rows: BR-3341, 3343, 3349, 3353, 3355, 3359, 3365 = 7. Answer: 7 builds.
2. Turn 2: per-repo split of those seven: vision-core 3 (3341, 3349, 3355), nav-stack 2, slam-maps 1, path-planner 1. Answer: vision-core.
3. Turn 3: measured durations over 900 s: BR-3343 (1042), BR-3349 (1102), BR-3355 (926), BR-3365 (954) = 4; the two null rows have no measured runtime. Answer: 4 builds.
4. Turn 4: drop the vision-core experimental run (BR-3349, channel=experimental): 4 - 1 = 3. Answer: 3 builds.

## Why the answer is unique
Every row carries one event and one repo, so the failure count and its per-repo split (3-2-1-1) are fixed. The README defines duration_s=null as "no runtime measured", which disqualifies folding the killed builds into the 900-second comparison; the naive reading that does so is the recorded decoy. The exclusion removes exactly BR-3349, leaving 3.
