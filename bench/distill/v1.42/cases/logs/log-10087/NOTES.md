## Traps
- Answer: 100. TR-DECOY: a substring grep for cam-3 gives 365.
- TR-MULTISRC: 6 files; the first one alone gives 12.
- Data volume: 6 data files, 90 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat cams/*.log | grep ' cam=cam-3 ' | grep -c 'event=offline'` -> 100
Final answer: cam-3 went offline 100 times.

## Why the answer is unique
cam is an exact key=value field.
