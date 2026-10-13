## Traps
- Answer: 3718. TR-DECOY: prefix-matching P-770 and P-77X gives 10637.
- TR-MULTISRC: 7 files; the first one alone gives 590.
- Data volume: 7 data files, 77 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat sales/lines/*.csv | awk -F, '$2=="P-77" {s+=$3} END {print s}'` -> 3718
Final answer: 3718 units of P-77.

## Why the answer is unique
product is an exact field.
