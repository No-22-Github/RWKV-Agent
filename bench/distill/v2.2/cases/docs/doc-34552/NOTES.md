## Traps
TR-TRUNC, TR-DECOY

## Reference solution
list_files 看各文件行数（defect-tracker/ledgerline-defects.md 599 行、defect-tracker/orchard-mobile-defects.md 704 行、defect-tracker/tidewater-api-defects.md 844 行）
search_text / bash grep 定位级别为高的条目，再读对应位置确认状态
read_file 用 start_line/end_line 读相关片段，约 4 次
write_file 写入 p0-open-defects.md，列出 7 个编号
作答。

## Why the answer is unique
Target entries are the only ones with level high, status open; decoys differ in exactly one field.

## Estimated trajectory tokens
12460
(fixture: defect-tracker/ledgerline-defects.md=4311, defect-tracker/orchard-mobile-defects.md=5162, defect-tracker/tidewater-api-defects.md=6180)
lines per document: [599, 704, 844]

## Five alternative phrasings of the task
1. Three defect lists live under defect-tracker. Find every P0 defect that is still unresolved, group them by product, and save id, title and owner in p0-open-defects.md.
2. 麻烦帮我：Three defect lists live under defect-tracker. Find every P0 defect that is still unresolved, group them by product, and save id, title and owner in p0-open-defects.md.
3. Three defect lists live under defect-tracker. Find every P0 defect that is still unresolved, group them by product, and save id, title and owner in p0-open-defects.md. (keep it organised)
4. 想请你看看：Three defect lists live under defect-tracker. Find every P0 defect that is still unresolved, group them by product, and save id, title and owner in p0-open-defects.md.
5. 再确认一下：Three defect lists live under defect-tracker. Find every P0 defect that is still unresolved, group them by product, and save id, title and owner in p0-open-defects.md.
