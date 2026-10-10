## Traps
- 核载 19 人包括教师和司机，学生只有 16 个座位。

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：小巴学生座位是 16 个（校车/运行手册.md）；核载 19 人里还包含随车教师和司机。
判据见 case.json（contains=[] any=['16 个', '16 名', '16 位', '16个', '16名', '16位'] excl=['最多 19', '最多能坐 19', '19 个学生']）。

## Why the answer is unique
题问学生，手册明确学生座位 16。
