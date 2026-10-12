## Traps
- Turn 1: exact answer 113; the loose reading (库、语句前缀匹配且阈值不含2000) gives 130.
- Turn 2: exact answer 106; the loose reading (库前缀匹配且阈值不含2000) gives 89.
- Turn 3: exact answer 35; the loose reading (语句前缀匹配且阈值不含2000) gives 42.
- TR-TRUNC: the file is 92KB and 1345 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `awk -F';' '$2=="orders" && $3=="SELECT" && $4>=2000 {c++} END{print c+0}' 慢查询/slow.txt` -> 113
Turn 2: bash: `awk -F';' '$2=="orders" && $3=="UPDATE" && $4>=2000 {c++} END{print c+0}' 慢查询/slow.txt` -> 106
Turn 3: bash: `awk -F';' '$2=="users" && $3=="SELECT" && $4>=2000 {a++} $2=="orders" && $3=="SELECT" && $4>=2000 {b++} END{d=a-b; if (d<0) d=-d; print d}' 慢查询/slow.txt` -> 35
Final answer: users 与 orders 的慢 SELECT 条数相差 35。

## Why the answer is unique
库 and 语句 are whole-value columns and the threshold is inclusive at 2000. The README (慢查询/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. users 库慢 SELECT 的条数和 orders 库的差多少？
2. 算出 users 的慢 SELECT 条数，再给我它与 orders 的差值。
3. 两个库的慢 SELECT 数量（users 对 orders）相差几条？
4. users 比 orders 多或少多少条慢 SELECT，取绝对值。
5. users 慢 SELECT 条数减去 orders 的，答案取绝对值。
