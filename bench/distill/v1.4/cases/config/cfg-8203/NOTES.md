## Traps
- 工作日和节假日费率不同，要取 weekend 段。

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：周末每小时 9 元（停车场/费率.toml 的 weekend 段），封顶 60 元；工作日是 6 元、节假日是 12 元。
判据见 case.json（contains=[] any=['9 元', '9 块', '9元', '9块'] excl=[]）。

## Why the answer is unique
周末费率只有 weekend 段一个值 9；6 和 12 分别是工作日和节假日。
