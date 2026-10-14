## Traps
- Answer: 175.
- TR-MULTISRC: 6 files; the first one alone gives 29.
- Data volume: 6 data files, 81 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat wms/moves/*.tsv | awk -F'\t' '$4=="in" && $3>=80' | wc -l` -> 175
Final answer: 175 inbound movements of 80+.

## Why the answer is unique
sku and direction are exact tab-separated fields.
