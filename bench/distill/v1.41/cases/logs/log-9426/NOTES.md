## Traps
- TR-DECOY: exact answer 269; the loose reading (补跑标记被当作正式窗口) gives 58.
- TR-TRUNC: the file is 57KB and 1174 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk -F'\t' '$2=="MARK" && $3=="对账开始" {k++; if (k==3) on=1; next} $2=="MARK" && $3=="对账结束" {on=0} on {c++} END{print c+0}' 对账/作业.txt` -> 269
Final answer: 第三个正式窗口内有 269 行。

## Why the answer is unique
Windows are delimited by exact MARK rows; the re-run markers are excluded, so the third official window is unambiguous. The README (对账/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 作业.txt 第 3 个对账窗口里有多少行日志？
2. 不算补跑，第三次对账开始到对账结束之间的行数。
3. 按说明.md，当天第三个正式窗口包含几行？
4. 统计第三个「对账开始」与其后「对账结束」之间的行数（补跑标记除外）。
5. 第三个对账窗口里一共记录了多少行？
