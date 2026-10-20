## Traps
TR-TRUNC, TR-DECOY

## Reference solution
list_files 看各文件行数（缺陷库/云账本-缺陷清单.md 592 行、缺陷库/智巡-缺陷清单.md 676 行、缺陷库/灯塔-缺陷清单.md 480 行）
search_text / bash grep 定位级别为高的条目，再读对应位置确认状态
read_file 用 start_line/end_line 读相关片段，约 4 次
write_file 写入 发版阻塞项.md，列出 7 个编号
作答。

## Why the answer is unique
Target entries are the only ones with level high, status open; decoys differ in exactly one field.

## Estimated trajectory tokens
14260
(fixture: 缺陷库/云账本-缺陷清单.md=6834, 缺陷库/智巡-缺陷清单.md=7929, 缺陷库/灯塔-缺陷清单.md=5593)
lines per document: [592, 676, 480]

## Five alternative phrasings of the task
1. 发版前要清一下 P0。三份缺陷清单在缺陷库目录，请把优先级是 P0 且还待修复的缺陷整理出来，写到 发版阻塞项.md，包含编号、标题和负责人。
2. 麻烦帮我：发版前要清一下 P0。三份缺陷清单在缺陷库目录，请把优先级是 P0 且还待修复的缺陷整理出来，写到 发版阻塞项.md，包含编号、标题和负责人。
3. 发版前要清一下 P0。三份缺陷清单在缺陷库目录，请把优先级是 P0 且还待修复的缺陷整理出来，写到 发版阻塞项.md，包含编号、标题和负责人。（用中文回答）
4. 想请你看看：发版前要清一下 P0。三份缺陷清单在缺陷库目录，请把优先级是 P0 且还待修复的缺陷整理出来，写到 发版阻塞项.md，包含编号、标题和负责人。
5. 再确认一下：发版前要清一下 P0。三份缺陷清单在缺陷库目录，请把优先级是 P0 且还待修复的缺陷整理出来，写到 发版阻塞项.md，包含编号、标题和负责人。
