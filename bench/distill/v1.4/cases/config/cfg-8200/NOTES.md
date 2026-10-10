## Traps
- 归档目录里有去年的旧规则（21:00），要用现行文件。

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：山栖民宿现行规则是最晚 22:00 办完入住（规则/入住.yaml）；归档里去年的旧版是 21:00，已不适用。
判据见 case.json（contains=[] any=['22:00', '22 点', '22点', '晚上 10 点', '晚上10点', '十点'] excl=[]）。

## Why the answer is unique
现行文件只有一个最晚入住时间；归档文件的 21:00 是去年的旧值。
