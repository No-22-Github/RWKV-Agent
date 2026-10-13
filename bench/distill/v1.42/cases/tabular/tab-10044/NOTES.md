## Traps
- Answer: S-20.
- TR-MULTISRC: 6 files; the first one alone gives S-13.
- Data volume: 6 data files, 79 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat wms/moves/*.tsv | awk -F'\t' '$4=="in" {a[$5]+=$3} END {for (k in a) print a[k], k}' | sort -rn | head -3` -> S-20
Final answer: Bin S-20 received the most.

## Why the answer is unique
sku and direction are exact tab-separated fields.
