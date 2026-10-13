## Traps
- Turn 1: 308. TR-DECOY: counting 大件拆分 gives 442.
- Turn 2: 96.
- TR-MULTISRC: 8 files; the first one alone gives 12.
- Data volume: 8 data files, 83 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
Turn 1: bash: `cat 快递/揽收/*.csv | awk -F, '$4=="大件"' | wc -l` -> 308
Turn 2: bash: `cat 快递/揽收/*.csv | awk -F, '$4=="大件" && $3>30' | wc -l` -> 96
Final answer (last turn): 超过 30kg 的大件有 96 件。

## Why the answer is unique
件型和状态是精确字段；字段说明写明大件拆分不算大件。
