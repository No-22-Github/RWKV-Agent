## Traps
- TR-HEADER: the trial sheet ends with a `TOTAL` line summing every cultivar. Taking the largest value in the
  seedlings column without stepping past that line gives 2754 instead of 87.

## Reference solution
1. List the workspace: the trial sheet and a short readme.
2. Read seedling_trial_june_2026.csv and step past the last line, which is labelled `TOTAL`.
3. The largest seedlings count among the 45 cultivars is Fanal's 87.

## Why the answer is unique
The readme states one row per cultivar, so each of the 45 cultivar rows is a separate entry and no two rows share a
cultivar name. The final `TOTAL` line describes the whole trial, not a cultivar, so it cannot be the best
cultivar's count. That leaves 87 as the largest per-cultivar figure.
