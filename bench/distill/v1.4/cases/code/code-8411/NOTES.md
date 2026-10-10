## Traps
- `max_upload_mb` 在同一文件里还有注释提及和 `max_upload_mb_legacy` 旧键；兄弟配置文件里还有同名键。只有主文件里一行以 `max_upload_mb = ` 开头。

## Reference solution
1. search_text 搜 `<键名> =`（限定题面给的文件路径），结果自带行号：第 337 行。
终答一句话：配置项在第 337 行。判据：任一行号写法；用过 search_text；read_file 最多 1 次。答案 337。

## Why the answer is unique
题面限定了文件，文件内只有一行以 `键名 = ` 开头。
