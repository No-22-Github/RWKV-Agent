## Traps
- TR-DECOY: exact answer 79; the loose match (工单号前缀匹配，含W-30210、W-3021B) gives 137.
- TR-TRUNC: the file is 44KB and 1196 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk -F'\t' '$2=="W-3021" && $3=="转派"' 工单/events.txt | wc -l` -> 79
Final answer: W-3021 被转派 79 次。

## Why the answer is unique
工单 and 事件 are whole-value columns. The README (工单/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. W-3021 这张工单的转派事件有几条？
2. events.txt 里工单号恰好是 W-3021、事件是转派的行数。
3. 按说明.md，W-3021 一共转派了多少次？
4. 统计工单 W-3021 的转派次数。
5. W-3021（不是 W-30210）被转派了几次？
