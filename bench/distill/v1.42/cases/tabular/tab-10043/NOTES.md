## Traps
- Answer: 14262. TR-DECOY: prefix-matching AX-1000 gives 29820.
- TR-MULTISRC: 6 files; the first one alone gives 2796.
- Data volume: 6 data files, 81 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat wms/moves/*.tsv | awk -F'\t' '$2=="AX-100" && $4=="out" {s+=$3} END {print s}'` -> 14262
Final answer: 14262 units of AX-100 shipped out (AX-1000 excluded).

## Why the answer is unique
sku and direction are exact tab-separated fields.
