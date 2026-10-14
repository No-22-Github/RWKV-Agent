## Traps
- TR-DECOY: exact answer 310760; the loose reading (用了第一个（草稿）区段) gives 206980.
- TR-TRUNC: the file is 64KB and 1191 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk '$2=="段" && $3=="第二季度开始" {k++; if (k==2) on=1; next} $2=="段" && $3=="第二季度结束" {on=0} on && $2=="财务部" {s+=$4} END{print s+0}' 账本/流水.txt` -> 310760
Final answer: 正式第二季度区段里财务部金额合计 310760。

## Why the answer is unique
The section name occurs twice and the README names the second one as official; 部门 is a whole-value column. The README (账本/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 流水.txt 第二个二季度区段里，财务部花了多少钱？
2. 草稿期不算，正式第二季度区段内部门是财务部的金额求和。
3. 按说明.md，正式记账区段里财务部的金额总和。
4. 第二次出现的「第二季度开始」到「第二季度结束」之间，财务部的金额加起来是多少？
5. 统计正式二季度区段内财务部（不含外包）的金额合计。
