## Traps
- no_show_fee 是爽约费，不是晚取消费。

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：晚取消要扣 35 元（studio/policy.json 的 late_cancel_fee）；爽约不到场是 60 元。
判据见 case.json（contains=[] any=['35 元', '35 块', '35元', '35块'] excl=[]）。

## Why the answer is unique
晚取消对应 late_cancel_fee = 35。
