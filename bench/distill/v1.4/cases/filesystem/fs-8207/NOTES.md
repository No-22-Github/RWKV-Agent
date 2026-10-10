## Traps
- Other records only list passes.

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：The failure is in calibration/2026-06.txt: gauge G-12 failed and was replaced.
判据见 case.json（contains=['2026-06'] any=[] excl=[]）。

## Why the answer is unique
Only 2026-06.txt contains FAILED.
