## Traps
- 三档退款比例，5 天落在中间档。

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：入住前 5 天退订属于「3 到 7 天」档，退 50%（营地/预订须知.md）。
判据见 case.json（contains=[] any=['50%', '50 %', '五成', '一半', '50％', '百分之五十'] excl=[]）。

## Why the answer is unique
5 天介于 3 到 7 天之间，只对应 50%。
