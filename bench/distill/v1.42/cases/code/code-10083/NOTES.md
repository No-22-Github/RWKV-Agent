## Traps
- Answer: 912. TR-DECOY: an unanchored grep fix gives 2225.
- TR-MULTISRC: 6 files; the first one alone gives 147.
- Data volume: 6 data files, 77 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat changelog/*.md | grep -cE '^- fix(:|\()'` -> 912
Final answer: 912 bug fix entries.

## Why the answer is unique
The README defines the match; one pattern gives one count.
