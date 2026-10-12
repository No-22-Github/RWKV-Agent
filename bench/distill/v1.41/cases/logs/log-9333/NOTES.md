## Traps
- Turn 1: exact answer 17; the loose reading (第一个开始标记是演练、级别前缀匹配) gives 20.
- Turn 2: exact answer 19; the loose reading (第一个开始标记是演练、级别前缀匹配) gives 16.
- TR-TRUNC: the file is 72KB and 1225 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `awk -F'\t' '$2=="MARK" && $4=="灰度发布开始" {on=1; next} $2=="MARK" && $4=="灰度发布结束" {on=0} on && $2=="ERROR" {c++} END{print c+0}' 发布/release.txt` -> 17
Turn 2: bash: `awk -F'\t' '$2=="MARK" && $4=="灰度发布开始" {on=1; next} $2=="MARK" && $4=="灰度发布结束" {on=0} on && $2=="WARN" {c++} END{print c+0}' 发布/release.txt` -> 19
Final answer: 灰度窗口内有 19 条 WARN。

## Why the answer is unique
The window is delimited by two exact MARK rows and levels are whole values. The README (发布/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 灰度窗口里 WARN 日志的条数。
2. 开始到结束之间级别是 WARN 的有几行？
3. 按说明.md，真正的灰度窗口内 WARN 一共多少条？
4. release.txt 灰度发布期间的 WARN 数量（WARN-SLOW 不算）。
5. 同样的窗口，统计级别恰好为 WARN 的行数。
