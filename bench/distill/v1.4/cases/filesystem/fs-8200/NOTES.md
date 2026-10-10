## Traps
- 归档子目录里还有一个 csv，不应计入。

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：盘点目录下有 3 个月度盘点 csv：2026-07、2026-08 和 2026-09；归档里的 2025-12 不算。
判据见 case.json（contains=[] any=['3 个', '3 份', '3 张', '3个', '3份', '3张', '三个', '三份'] excl=[]）。

## Why the answer is unique
盘点/ 一级目录下 csv 共 3 个，归档里的 1 个排除。
