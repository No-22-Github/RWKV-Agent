## Traps
- props/photos is nested, not top-level.

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：There are 5 top-level folders: lighting, sound, costumes, props and scripts (README.md is a file).
判据见 case.json（contains=['5'] any=[] excl=[]）。

## Why the answer is unique
Five distinct first path segments among files inside folders.
