## Traps
- TR-RULEFILE: 计数口径在 notes/ops-memo.txt——只有 CLEARED 的派运单计入 depot standings，QA-HOLD 留在质量队列。不做口径过滤按行数排名会交出 GB-Eastfield（126 行，其中 26 行 QA-HOLD）；按 memo 口径 GB-Weirside 以 118 张 CLEARED 排第一，它的行段集中在导出尾部、超出 read_file 的 64 KB 截断线。

## Reference solution
1. read_file README.md：口径见 notes/ops-memo.txt。
2. read_lines notes/ops-memo.txt：QA-HOLD 不计入站点排名。
3. search_text "QA-HOLD" 定位持押行段，read_lines 核对分布。
4. 逐个站点 search_text 定位行段并计数：GB-Eastfield CLEARED 100 张，GB-Weirside CLEARED 118 张。
5. 按 memo 口径比较，胜者为 GB-Weirside。

## Why the answer is unique
decoy GB-Eastfield 的领先完全来自 26 张不计入 standings 的 QA-HOLD 单，与 memo 的口径矛盾；按 CLEARED 计数 GB-Weirside 的 118 张多于任何其他站点，且第一名无并列。答案唯一为 GB-Weirside。
