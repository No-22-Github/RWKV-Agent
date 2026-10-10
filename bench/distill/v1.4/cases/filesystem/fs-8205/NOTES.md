## Traps
- server.py mentions the name but only imports it.

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：RATE_LIMIT_PER_MIN is defined in src/limits.py (set to 120); src/server.py only imports it.
判据见 case.json（contains=['src/limits.py'] any=[] excl=[]）。

## Why the answer is unique
Only limits.py has an assignment line.
