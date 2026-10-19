## Traps
TR-TRUNC, TR-DECOY

## Reference solution
list_files 看各文件行数（客服/华中大区-客诉工单.md 550 行、客服/西南大区-客诉工单.md 648 行、客服/东北大区-客诉工单.md 452 行、客服/海外-客诉工单.md 739 行、客服/线上商城-客诉工单.md 564 行）
search_text / bash grep 定位级别为高的条目，再读对应位置确认状态
read_file 用 start_line/end_line 读相关片段，约 4 次
write_file 写入 紧急未办结工单.md，列出 10 个编号
作答。

## Why the answer is unique
Target entries are the only ones with level high, status open; decoys differ in exactly one field.

## Estimated trajectory tokens
14350
(fixture: 客服/华中大区-客诉工单.md=7027, 客服/西南大区-客诉工单.md=8211, 客服/东北大区-客诉工单.md=5812, 客服/海外-客诉工单.md=9558, 客服/线上商城-客诉工单.md=7095)
lines per document: [550, 648, 452, 739, 564]

## Five alternative phrasings of the task
1. 年底要复盘客诉。五个大区的工单文件在客服目录，找出紧急程度为紧急、仍在处理中的工单，按文件分组写到 紧急未办结工单.md，每条要编号、标题、跟进人。
2. 麻烦帮我：年底要复盘客诉。五个大区的工单文件在客服目录，找出紧急程度为紧急、仍在处理中的工单，按文件分组写到 紧急未办结工单.md，每条要编号、标题、跟进人。
3. 年底要复盘客诉。五个大区的工单文件在客服目录，找出紧急程度为紧急、仍在处理中的工单，按文件分组写到 紧急未办结工单.md，每条要编号、标题、跟进人。（用中文回答）
4. 想请你看看：年底要复盘客诉。五个大区的工单文件在客服目录，找出紧急程度为紧急、仍在处理中的工单，按文件分组写到 紧急未办结工单.md，每条要编号、标题、跟进人。
5. 再确认一下：年底要复盘客诉。五个大区的工单文件在客服目录，找出紧急程度为紧急、仍在处理中的工单，按文件分组写到 紧急未办结工单.md，每条要编号、标题、跟进人。
