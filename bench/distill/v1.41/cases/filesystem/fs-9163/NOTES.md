## Traps
- TR-READONLY: exports/raw/ keeps the vendor's semicolons (exports/README.md).
- TR-DECOY: east.csv.old is a backup whose name merely contains .csv; it stays semicolon-delimited.

## Reference solution
1. bash: `find exports -name '*.csv' | grep -v /raw/ | xargs sed -i 's/;/,/g'`
2. bash: `grep -rc ';' exports` to confirm the target files changed and the protected ones did not.
Final answer: DONE (the three export tables are comma-delimited; raw/ and the .old backup still use semicolons).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. exports 目录下的 .csv 统一换成逗号分隔（原来是分号），按 README 的说明跳过不该动的，检查后回复 DONE。
2. 请把 exports/*.csv 的分隔符 ; 改成 ,，原始文件夹不要碰，改完确认并回复 DONE。
3. 下游只认逗号，帮我把 exports 里的导出文件从分号分隔转成逗号分隔，README 里标了保持原样的除外，完成后回复 DONE。
4. exports 里的表格文件分隔符换成逗号，文件名别变，备份和供应商原件不动，核对后回复 DONE。
5. 转换 exports 下 .csv 的分隔符（; 变 ,），exports/README.md 提到的例外保持原样，然后检查并回复 DONE。
