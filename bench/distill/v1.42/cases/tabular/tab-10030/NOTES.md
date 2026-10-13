## Traps
- Turn 1: 233.
- Turn 2: 53.
- TR-MULTISRC: 8 files; the first one alone gives 7.
- Data volume: 8 data files, 76 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
Turn 1: bash: `cat grades/*.csv | awk -F, '$5=="2026S" && $3>=90' | wc -l` -> 233
Turn 2: bash: `cat grades/*.csv | awk -F, '$5=="2026S" && $3>=90 && $2=="CHEM120"' | wc -l` -> 53
Final answer (last turn): 53 CHEM120 scores of 90+ in 2026S.

## Why the answer is unique
course, attempt and term are exact fields; MATH1010 is a different course per the README.
