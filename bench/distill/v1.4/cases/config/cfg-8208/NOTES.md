## Traps
- The pale ale recipe has a similar mash temperature.

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：The Harbour Stout is mashed at 67 degrees C (recipes/stout.cfg); the pale ale uses 65.
判据见 case.json（contains=['67'] any=[] excl=[]）。

## Why the answer is unique
Only stout.cfg belongs to Harbour Stout.
