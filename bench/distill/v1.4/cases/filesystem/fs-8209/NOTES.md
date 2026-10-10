## Traps
- None beyond picking the right owner line.

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：Priya owns the irrigation task (tasks/irrigation.md), due 2026-03-01.
判据见 case.json（contains=['irrigation'] any=[] excl=[]）。

## Why the answer is unique
Only irrigation.md has Owner: Priya.
