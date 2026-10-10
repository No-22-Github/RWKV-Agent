## Traps
- 2 小时、4 小时是预约时长，不是取消期限。

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：开始前 24 小时以上取消不收费；不足 24 小时要收 50% 场地费（排练室/使用说明.md）。
判据见 case.json（contains=[] any=['24 小时', '24 个小时', '24小时', '24个小时'] excl=[]）。

## Why the answer is unique
取消条款只写了 24 小时。
