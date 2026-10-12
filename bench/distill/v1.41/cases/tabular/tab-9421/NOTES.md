## Traps
- TR-DECOY: exact answer 5972; the loose reading (第一个开始标记是试盘、类型前缀匹配含入库(退回)) gives 2987.
- TR-TRUNC: the file is 60KB and 1182 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk -F'\t' '$2=="段" && $3=="B区开始" {on=1; next} $2=="段" && $3=="B区结束" {on=0} on && $2=="入库" {s+=$4} END{print s+0}' 盘点/盘点单.dat` -> 5972
Final answer: B 区盘点期间入库数量合计 5972。

## Why the answer is unique
The section is delimited by two exact marker rows and the type is a whole-value column. The README (盘点/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 盘点单里 B 区正式盘点期间，入库的数量加起来是多少？
2. 从「B区开始」到「B区结束」，类型恰好是入库的行，数量列求和。
3. 按说明.md，B 区盘点窗口内入库数量总和。
4. 试盘不算，B 区真正盘点那一段里入库了多少件？
5. 统计 B 区盘点区段内类型为入库的数量合计。
