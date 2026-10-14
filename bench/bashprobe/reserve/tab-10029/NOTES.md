## Traps
- Answer: 201.
- TR-MULTISRC: 8 files; the first one alone gives 22.
- Data volume: 8 data files, 78 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat grades/*.csv | awk -F, '$2=="PHYS110" && $4>=2 {print $1}' | sort -u | wc -l` -> 201
Final answer: 201 students retook PHYS110.

## Why the answer is unique
course, attempt and term are exact fields; MATH1010 is a different course per the README.
