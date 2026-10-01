## Traps
- TR-DECOY: backup-2026-05-26-full-hotfix.sql 文件名带 full，但文件首行标注是 -- type: incremental（注释写明热修窗口只来得及做增量）。按文件名数会得到 7；按文件内首行标注数是 6。其余 9 个文件名与标注一致（full 5 个 + incremental 4 个），加上 05-26 共 incremental 5 个。

## Reference solution
1. 列出 backup 目录：10 个 .sql 文件。
2. 逐个打开看首行 -- type: 标注（或按首行检索）。
3. 标注为 full 的有 05-01、05-08、05-15、05-22、05-29、06-05 共 6 个；05-26 文件名带 full 但内容标注 incremental，不计入。

## Why the answer is unique
题面把口径定在「文件里的类型标注」，标注在每份文件首行、逐个唯一；唯一的名字与标注不一致的文件在注释里自己写明了原因。按标注计数 6 是唯一与全部首行一致的结果，按文件名数的 7 与 05-26 的首行标注直接矛盾。答案唯一为 6。
