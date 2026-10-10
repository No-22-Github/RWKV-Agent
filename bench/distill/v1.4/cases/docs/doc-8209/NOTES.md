## Traps
- Standard and Express allow 30 kg.

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：The economy service takes parcels up to 20 kg (guide/services.md).
判据见 case.json（contains=['20'] any=[] excl=[]）。

## Changelog
- v2：S5：去掉排除项 30 kg——老师说明 Standard/Express 是 30 kg 属解释性提及。

## Why the answer is unique
The Economy row says 20 kg.
