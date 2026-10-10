## Traps
- 60% is the withdrawal threshold, not the certificate threshold.

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：You need at least 80% attendance and a pass in the final assessment (handbook/certificates.md).
判据见 case.json（contains=[] any=['80%', '80 %', '80 percent', 'eighty percent'] excl=['at least 60%', 'need 60%']）。

## Why the answer is unique
The certificate line says 80%.
