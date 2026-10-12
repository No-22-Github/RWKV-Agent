## Traps
- TR-MULTISRC: 3 per-group tables; the first alone gives 67.
- TR-DECOY: 「已缴费退课」 contains 「已缴费」 as a substring; 报名/说明.md says the status is matched exactly, a substring match gives 355.
- TR-DEFN: aggregating every row regardless of status gives 575.

## Reference solution
1. bash: `cat 报名/2026秋/*.csv | awk -F, '$2=="已缴费"' | wc -l`
Final answer: 秋季三个校区状态恰好是「已缴费」的共 236 人（已缴费退课另算）。

## Why the answer is unique
The status is an exact field value, the README pins the criterion, all 3 files are aggregated.

## Alternative phrasings
1. 三个校区秋季报名里，缴了费、状态是已缴费的有多少个学生？按 报名/说明.md。
2. 报名目录下三张校区表，已缴费的行数合计是多少？
3. 按说明文件的口径，秋季已缴费的在读人数是多少？
4. 数一下秋季各校区报名表里状态为已缴费的学员总数。
5. 报名/说明.md 里写了怎么算已缴费人数，三个校区加起来是几个人？
