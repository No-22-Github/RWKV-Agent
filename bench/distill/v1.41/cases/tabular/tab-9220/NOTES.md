## Traps
- TR-READONLY: exports/archive keeps last year's column names (exports/README.md).
- TR-DECOY: data rows carry the note text `user_id mismatch`; a global replace would change them.

## Reference solution
1. bash: `find exports -name '*.csv' | grep -v /archive/ | xargs sed -i '1s/user_id/uid/'`
2. bash: `grep -rn user_id exports` to confirm the target files changed and the protected ones did not.
Final answer: DONE (the four monthly headers say uid; archive/2025.csv and the note text in data rows still say user_id).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. 把 exports 下月度 csv 的表头 user_id 改名为 uid，仅第一行，存档目录别动，检查后回复 DONE。
2. 批量改列名：exports/*.csv 首行的 user_id → uid，数据行里的文字保持原样，按 README 排除存档，完成后回复 DONE。
3. 请更新四个月的导出表头（user_id 换成 uid），其他行与 archive 保持不变，核对后回复 DONE。
4. exports 里除 archive 外的 csv，只把表头里的 user_id 列名换成 uid，改完确认并回复 DONE。
5. 各月 csv 的第一行列名 user_id 统一改成 uid，注意 note 列里的 user_id mismatch 文字不是列名，检查后回复 DONE。
