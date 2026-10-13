## Traps
- Answer: 4549.85. TR-DECOY: counting 大件拆分 as 大件 gives 6601.67.
- TR-MULTISRC: 8 files; the first one alone gives 559.07.
- Data volume: 8 data files, 75 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 快递/揽收/*.csv | awk -F, '$4=="大件" && $5=="已签收" {s+=$3} END {printf "%.2f\n", s}'` -> 4549.85
Final answer: 已签收大件总重 4549.85 kg（大件拆分不算）。

## Why the answer is unique
件型和状态是精确字段；字段说明写明大件拆分不算大件。
