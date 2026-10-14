## Traps
- Answer: 196. TR-DECOY: counting MATH1010 too gives 377.
- TR-MULTISRC: 8 files; the first one alone gives 22.
- Data volume: 8 data files, 79 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat grades/*.csv | awk -F, '$2=="MATH101" && $4==1 && $3<60' | wc -l` -> 196
Final answer: 196 first-attempt MATH101 results were below 60.

## Why the answer is unique
course, attempt and term are exact fields; MATH1010 is a different course per the README.
