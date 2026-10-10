## Traps
- Vehicles have a different cutoff (45).

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：Check-in closes 30 minutes before departure for foot passengers (faq/boarding.md); for vehicles it is 45 minutes.
判据见 case.json（contains=[] any=['30 minutes', '30 min', 'half an hour', 'half hour', '30-minute'] excl=[]）。

## Why the answer is unique
The question names foot passengers: 30.
