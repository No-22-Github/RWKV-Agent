## Traps
- None. 本轮没有写文件的工具。

## Reference solution
1. data_query：path logs/events-2026-09-15.jsonl，group_by level，operation count。得到 INFO 88、WARN 49、ERROR 28、FATAL 15。
终答 2–3 句：列出四个级别的计数，并说明本轮没有写文件的工具，没写进 统计/级别分布.txt，需要用户自己保存（给出可直接粘贴的几行）。判据：四个计数都作为独立词元出现，并有一个「没法写/需要你保存」说法。

## Why the answer is unique
level 字段只有四个取值，计数由文件唯一确定，合计 180。

## Changelog
- v2：「写不了文件」的说法词表补上「没法创建 / 无法创建 / 只读 / 没有写文件 / 没法追加」等。试跑里解题者写「只有只读工具，没法创建 X」，说明完全正确，却因词表太窄被判挂。
