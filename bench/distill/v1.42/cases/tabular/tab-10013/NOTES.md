## Traps
- Answer: 衢州.
- Data volume: 8 data files, 82 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 快递/揽收/*.csv | awk -F, '$5=="运输中" {print $2}' | sort | uniq -c | sort -rn | head -3` -> 衢州
Final answer: 运输中的件以 衢州 最多。

## Why the answer is unique
件型和状态是精确字段；字段说明写明大件拆分不算大件。
