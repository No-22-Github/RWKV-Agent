## Traps
- Answer: 613. TR-DECOY: an unescaped grep '[WARN]' (a character class) gives 3689.
- TR-MULTISRC: 6 files; the first one alone gives 108.
- Data volume: 6 data files, 79 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat logs/build/*.log | grep -cF '[WARN]'` -> 613
Final answer: 613 [WARN] lines.

## Why the answer is unique
The README defines the match; one pattern gives one count.
