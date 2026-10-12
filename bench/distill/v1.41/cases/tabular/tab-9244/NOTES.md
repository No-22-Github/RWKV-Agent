## Traps
- Turn 1: exact answer 70; the loose match (prefix match on branch and status) gives 142.
- Turn 2: exact answer 1730; the loose match (branch prefix match, includes release-2.1) gives 1779.
- TR-MULTISRC: 3 files; the first file alone gives 1730.
- Turn 2 needs a different filter over the same data, so turn 1's number is the wrong answer.

## Reference solution
Turn 1: bash: `cat ci/*.dat | awk '$2=="main" && $3=="failed"' | wc -l` -> 70
Turn 2: bash: `cat ci/*.dat | awk '$2=="release" && $3=="passed" && $4+0>m {m=$4+0} END{print m}'` -> 1730
Final answer: The longest passed run on release took 1730 seconds.

## Why the answer is unique
branch and status are whole-value columns of the space-separated export. The README (ci/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Longest passed run on the release branch, in seconds?
2. What is the max seconds among passed runs of branch release in the CI files?
3. Across the weekly CI files, how long was the slowest passed release run?
4. Max duration (seconds) for status passed on branch release, per ci/README.md.
5. Which duration in seconds is the largest for passed runs on release?
