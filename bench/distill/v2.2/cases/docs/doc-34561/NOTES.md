## Traps
TR-TRUNC, TR-DECOY

## Reference solution
list_files 看各文件行数（实验室/材料楼-设备报修.md 704 行、实验室/生物楼-设备报修.md 830 行、实验室/信息楼-设备报修.md 634 行）
search_text / bash grep 定位级别为高的条目，再读对应位置确认状态和负责人
read_file 用 start_line/end_line 读相关片段，约 4 次
write_file 写入 周杰-一级未修复.md，列出 6 个编号
作答。

## Why the answer is unique
Target entries are the only ones with level high, status open and the named owner; decoys differ in exactly one field.

## Estimated trajectory tokens
14230
(fixture: 实验室/材料楼-设备报修.md=9044, 实验室/生物楼-设备报修.md=10630, 实验室/信息楼-设备报修.md=8091)
lines per document: [704, 830, 634]

## Five alternative phrasings of the task
1. 后勤处在清理积压报修。实验室目录下有三栋楼的设备报修记录，帮我找出故障等级为一级、还没修复、并且报修人是 周杰 的记录，把编号和标题写到 周杰-一级未修复.md。
2. 麻烦帮我：后勤处在清理积压报修。实验室目录下有三栋楼的设备报修记录，帮我找出故障等级为一级、还没修复、并且报修人是 周杰 的记录，把编号和标题写到 周杰-一级未修复.md。
3. 后勤处在清理积压报修。实验室目录下有三栋楼的设备报修记录，帮我找出故障等级为一级、还没修复、并且报修人是 周杰 的记录，把编号和标题写到 周杰-一级未修复.md。（用中文回答）
4. 想请你看看：后勤处在清理积压报修。实验室目录下有三栋楼的设备报修记录，帮我找出故障等级为一级、还没修复、并且报修人是 周杰 的记录，把编号和标题写到 周杰-一级未修复.md。
5. 再确认一下：后勤处在清理积压报修。实验室目录下有三栋楼的设备报修记录，帮我找出故障等级为一级、还没修复、并且报修人是 周杰 的记录，把编号和标题写到 周杰-一级未修复.md。
