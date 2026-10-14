## Traps
- Turn 1: 1005.
- Turn 2: 932. TR-DECOY: an unanchored grep fix gives 2397.
- TR-MULTISRC: 6 files; the first one alone gives 151.
- Data volume: 6 data files, 83 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
Turn 1: bash: `cat changelog/*.md | grep -cE '^- feat(:|\()'` -> 1005
Turn 2: bash: `cat changelog/*.md | grep -cE '^- fix(:|\()'` -> 932
Final answer (last turn): 932 bug fix entries.

## Why the answer is unique
The README defines the match; one pattern gives one count.
