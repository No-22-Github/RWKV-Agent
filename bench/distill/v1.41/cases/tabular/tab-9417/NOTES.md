## Traps
- TR-DECOY: exact answer 1692; the loose reading (prefix match on turbine and mode) gives 2083.
- TR-MULTISRC: 3 files; the first file alone gives 1638.

## Reference solution
Turn 1: bash: `cat turbines/*.dat | awk '$2=="T-07" && $3=="run" {print $4}' | sort -rn | head -1` -> 1692
Final answer: 1692 rpm.

## Why the answer is unique
turbine and mode are whole-value columns. The README (turbines/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Peak rpm for T-07 in run mode?
2. Maximum rpm where turbine is T-07 and mode is run.
3. Per turbines/README.md, how fast did T-07 spin at most in run mode?
4. Highest rpm reading of T-07 (mode run only).
5. What is T-07's top rpm across the three sites, run mode?
