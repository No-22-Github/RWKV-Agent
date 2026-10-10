## Traps
- 电池和主板的保修期不同。

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：换屏保修 90 天，但人为摔坏和进水不在保修范围（店规/保修.md）。
判据见 case.json（contains=[] any=['90 天', '90 日', '90天', '90日'] excl=[]）。

## Why the answer is unique
换屏一行写明 90 天。
