## Traps
- default.yaml says 10; production overrides it.

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：Production uses a pool size of 40: config/production.yaml overrides the default of 10.
判据见 case.json（contains=['40'] any=[] excl=['size of 10', 'size is 10']）。

## Why the answer is unique
Only production.yaml sets the production pool size.
