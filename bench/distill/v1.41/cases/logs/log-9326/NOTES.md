## Traps
- TR-DECOY: exact answer 40; the loose reading (prefix match on build and event) gives 46.
- TR-MULTISRC: 3 files; the first file alone gives 17.

## Reference solution
Turn 1: bash: `cat crashes/*.txt | awk -F, '$2=="4.2.0" && $4=="crash" {print $3}' | sort -u | wc -l` -> 40
Final answer: 40 distinct device models crashed on 4.2.0.

## Why the answer is unique
build and event are whole-value columns; device models are de-duplicated across files. The README (crashes/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Count the unique devices with event crash on build 4.2.0.
2. How many distinct device models crashed on 4.2.0 (rc builds excluded)?
3. Across the weekly crash feeds, number of different models with a real crash on build 4.2.0.
4. Per crashes/README.md, how many device models hit a crash on 4.2.0?
5. De-duplicated device count for build 4.2.0 and event crash.
