## Traps
- Answer: MATH1010.
- Data volume: 8 data files, 81 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat grades/*.csv | awk -F, '$5=="2026S" && $3<60 {print $2}' | sort | uniq -c | sort -rn | head -3` -> MATH1010
Final answer: MATH1010 had the most fails in 2026S.

## Why the answer is unique
course, attempt and term are exact fields; MATH1010 is a different course per the README.
