## Traps
- 预约和取消条款里也有天数，不是理赔时限。

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：签收后 48 小时内要提出理赔，超过就不再受理（条款/服务条款.md 第二章）；贵重物品需事先申报。
判据见 case.json（contains=[] any=['48 小时', '48 个小时', '48 h', '48小时', '48个小时', '48h'] excl=[]）。

## Why the answer is unique
理赔时限只在第二章写了一次：48 小时。
