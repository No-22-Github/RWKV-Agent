## Traps
- The $12 fee is for extra guests beyond the free ones.

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：You can bring up to 3 guests a month for free (handbook/guests.md); extra guests cost $12 a day.
判据见 case.json（contains=['3'] any=[] excl=[]）。

## Why the answer is unique
Free guests are capped at 3 per month.
