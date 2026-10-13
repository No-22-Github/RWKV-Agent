## Traps
- Turn 1: 6.
- Turn 2: 13537.
- TR-MULTISRC: 6 files; the first one alone gives 2570.
- Data volume: 6 data files, 76 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
Turn 1: bash: `awk -F'\t' '$4=="out" {print $2}' wms/moves/2026-09.tsv | sort -u | wc -l` -> 6
Turn 2: bash: `cat wms/moves/*.tsv | awk -F'\t' '$2=="DZ-045" && $4=="out" {s+=$3} END {print s}'` -> 13537
Final answer (last turn): 13537 units of DZ-045 went out.

## Why the answer is unique
sku and direction are exact tab-separated fields.
