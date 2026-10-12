## Traps
- TR-READONLY: reports/外部 holds partner originals that the interface reads pipe-delimited (reports/README.md).
- TR-DECOY: q1.dat.orig is an old backup whose name contains .dat.

## Reference solution
1. bash: `find reports -name '*.dat' | grep -v /外部/ | xargs sed -i 's/|/,/g'`
2. bash: `grep -rc '|' reports` to confirm the target files changed and the protected ones did not.
Final answer: DONE (q1 to q4 are comma-delimited; the partner file and the .orig backup still use pipes).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. reports 下的 .dat 表格分隔符由 | 换成 ,，合作方文件夹和备份不动，改完核对并回复 DONE。
2. 请把内部报表（reports/*.dat）转成逗号分隔，别改文件名，README 里的例外保持原样，检查后回复 DONE。
3. 批量转换 reports 里 .dat 的列分隔符：竖线改逗号，reports/外部 不碰，完成后确认并回复 DONE。
4. 四个季度报表的分隔符从竖线改成逗号，其余文件保持不变，参照 reports/README.md，检查后回复 DONE。
5. reports 目录中除外部原件之外的 .dat 改用逗号分隔，然后检查并回复 DONE。
