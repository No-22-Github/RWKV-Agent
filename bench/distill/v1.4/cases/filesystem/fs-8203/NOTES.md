## Traps
- 三个日志格式相同，只有一个含停转记录。

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：是塘 B：日志/塘B.log 里 13:20 记了增氧机停转并已报修。
判据见 case.json（contains=[] any=['塘B', '塘 B', 'B 塘', 'B塘'] excl=[]）。

## Why the answer is unique
只有 塘B.log 含「增氧机停转」。
