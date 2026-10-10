## Traps
- nightly.yml has a different retry count.

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：On a normal push a failing integration test is retried 2 times (.ci/pipeline.yml); the nightly run allows 5.
判据见 case.json（contains=['2'] any=[] excl=['retried 5', '5 times on a normal']）。

## Why the answer is unique
Normal pushes use pipeline.yml, which sets 2.
