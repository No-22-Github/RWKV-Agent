## Traps
TR-TRUNC, TR-DECOY

## Reference solution
list_files 看各文件行数（项目风险/青岚平台-风险登记簿.md 508 行、项目风险/海豚结算-风险登记簿.md 669 行、项目风险/远帆门户-风险登记簿.md 774 行）
search_text / bash grep 定位级别为高的条目，再读对应位置确认状态
read_file 用 start_line/end_line 读相关片段，约 4 次
write_file 写入 高风险未关闭清单.md，列出 7 个编号
作答。

## Why the answer is unique
Target entries are the only ones with level high, status open; decoys differ in exactly one field.

## Estimated trajectory tokens
14260
(fixture: 项目风险/青岚平台-风险登记簿.md=6038, 项目风险/海豚结算-风险登记簿.md=7942, 项目风险/远帆门户-风险登记簿.md=9364)
lines per document: [508, 669, 774]

## Five alternative phrasings of the task
1. 我要给周会准备材料。三个项目的风险登记簿都在项目风险文件夹里，帮我找出所有级别为高、状态还没关闭的风险，按项目分组列出编号、标题和负责人，写到 高风险未关闭清单.md。
2. 麻烦帮我：我要给周会准备材料。三个项目的风险登记簿都在项目风险文件夹里，帮我找出所有级别为高、状态还没关闭的风险，按项目分组列出编号、标题和负责人，写到 高风险未关闭清单.md。
3. 我要给周会准备材料。三个项目的风险登记簿都在项目风险文件夹里，帮我找出所有级别为高、状态还没关闭的风险，按项目分组列出编号、标题和负责人，写到 高风险未关闭清单.md。（用中文回答）
4. 想请你看看：我要给周会准备材料。三个项目的风险登记簿都在项目风险文件夹里，帮我找出所有级别为高、状态还没关闭的风险，按项目分组列出编号、标题和负责人，写到 高风险未关闭清单.md。
5. 再确认一下：我要给周会准备材料。三个项目的风险登记簿都在项目风险文件夹里，帮我找出所有级别为高、状态还没关闭的风险，按项目分组列出编号、标题和负责人，写到 高风险未关闭清单.md。
