## Traps
TR-TRUNC, TR-DECOY

## Reference solution
list_files 看各文件行数（programme/atlas-risk-register.md 634 行、programme/beacon-risk-register.md 739 行、programme/cairn-risk-register.md 529 行、programme/dune-risk-register.md 830 行）
search_text / bash grep 定位级别为高的条目，再读对应位置确认状态和负责人
read_file 用 start_line/end_line 读相关片段，约 4 次
write_file 写入 priya-open-high.md，列出 7 个编号
作答。

## Why the answer is unique
Target entries are the only ones with level high, status open and the named owner; decoys differ in exactly one field.

## Estimated trajectory tokens
12460
(fixture: programme/atlas-risk-register.md=4793, programme/beacon-risk-register.md=5635, programme/cairn-risk-register.md=4032, programme/dune-risk-register.md=6382)
lines per document: [634, 739, 529, 830]

## Five alternative phrasings of the task
1. For the steering group: pull out the high-severity risks that are still open and owned by Priya Nair across the four registers in the programme folder, and write their ids and titles to priya-open-high.md.
2. 麻烦帮我：For the steering group: pull out the high-severity risks that are still open and owned by Priya Nair across the four registers in the programme folder, and write their ids and titles to priya-open-high.md.
3. For the steering group: pull out the high-severity risks that are still open and owned by Priya Nair across the four registers in the programme folder, and write their ids and titles to priya-open-high.md. (keep it organised)
4. 想请你看看：For the steering group: pull out the high-severity risks that are still open and owned by Priya Nair across the four registers in the programme folder, and write their ids and titles to priya-open-high.md.
5. 再确认一下：For the steering group: pull out the high-severity risks that are still open and owned by Priya Nair across the four registers in the programme folder, and write their ids and titles to priya-open-high.md.
