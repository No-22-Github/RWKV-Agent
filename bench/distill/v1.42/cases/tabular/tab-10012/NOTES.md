## Traps
- Answer: 17.
- TR-MULTISRC: 8 files; the first one alone gives 1.
- Data volume: 8 data files, 86 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 快递/揽收/*.csv | awk -F, '$2=="温州" && $5=="退回"' | wc -l` -> 17
Final answer: 寄往温州的退回件共 17 件。

## Why the answer is unique
件型和状态是精确字段；字段说明写明大件拆分不算大件。
