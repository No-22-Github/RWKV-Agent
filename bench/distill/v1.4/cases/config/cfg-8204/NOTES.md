## Traps
- 试验.env 是另一个蜂场，取蜜间隔不同。

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：正式蜂场每 9 天取一次蜜（养蜂场/prod.env）；试验蜂场的 5 天只用于新蜂种试验。
判据见 case.json（contains=[] any=['9 天', '9 日', '9天', '9日'] excl=[]）。

## Why the answer is unique
题问正式蜂场，对应 prod.env 的 9 天。
