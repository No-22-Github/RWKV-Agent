## Traps
- `buildCartSummary` 在同一文件里还有注释提及、调用处和带 v1 / Old / Legacy 后缀的弃用旧实现；兄弟文件里还有一个同名函数。只有主文件里那一行以完整签名开头。

## Reference solution
1. search_text 搜 `<定义关键字> <函数名>(`（限定题面给的文件路径），结果自带行号：第 410 行。
终答一句话：定义在第 410 行（注释、调用处、旧实现和兄弟文件的同名函数都不是）。判据：任一行号写法；用过 search_text；read_file 最多 1 次。答案 410。

## Why the answer is unique
题面限定了文件，文件内只有一行以完整定义签名开头。
