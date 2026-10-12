## Traps
- Turn 1: exact answer 23; the loose reading (第一个开始标记是演练、级别前缀匹配) gives 19.
- Turn 2: exact answer 12; the loose reading (第一个开始标记是演练) gives 5.
- Turn 3: exact answer 9; the loose reading (第一个开始标记是演练) gives 4.
- TR-TRUNC: the file is 75KB and 1165 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `awk -F';' '$2=="MARK" && $4=="盘点开始" {on=1; next} $2=="MARK" && $4=="盘点结束" {on=0} on && $2=="差异" {c++} END{print c+0}' 盘点/现场记录.txt` -> 23
Turn 2: bash: `awk -F';' '$2=="MARK" && $4=="盘点开始" {on=1; next} $2=="MARK" && $4=="盘点结束" {on=0} on && $2=="漏扫" {c++} END{print c+0}' 盘点/现场记录.txt` -> 12
Turn 3: bash: `awk -F';' '$2=="MARK" && $4=="盘点开始" {on=1; next} $2=="MARK" && $4=="盘点结束" {on=0} on && $2=="待复核" {a++} on && $2=="漏扫" {b++} END{d=a-b; if (d<0) d=-d; print d}' 盘点/现场记录.txt` -> 9
Final answer: 待复核与漏扫的条数相差 9。

## Why the answer is unique
The window is delimited by two exact MARK rows and levels are whole values. The README (盘点/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 窗口内待复核和漏扫的条数差多少？
2. 算出待复核的条数，再给我它与漏扫条数的差值。
3. 盘点窗口里待复核比漏扫多（或少）多少条，取绝对值。
4. 待复核与漏扫两种级别在窗口内的数量差距。
5. 待复核条数减漏扫条数，答案取绝对值。
