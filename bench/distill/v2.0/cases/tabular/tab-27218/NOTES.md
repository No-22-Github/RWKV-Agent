## Traps
- TR-DUPROW: 导出重试把 26 行会话在同一 session_id 下整行重发（AD-Quay-02 的行段里）。AD-Quay-02 以 126 行位居行数第一（其中只有 100 个不同司机）；按行数排名会交出 AD-Quay-02。题面问不同司机数：AD-Slip-05 以 118 个不同司机排第一，它的行段集中在导出尾部、超出 read_file 的 64 KB 截断线。

## Reference solution
1. read_file README.md：重发行同 session_id，行数不是司机数。
2. read_lines 抽样表头附近，确认列格式与站点代码清单。
3. search_text "AD-Quay-02"（行数最多的候选）：126 行，只有 100 个不同司机。
4. search_text "AD-Slip-05"：118 行，全部是不同司机，行段在文件尾部。
5. 其余站点逐一检索同法核对，均不足 118 个不同司机；胜者为 AD-Slip-05。

## Why the answer is unique
decoy AD-Quay-02 只在行数上领先，多出的 26 行是逐字节重复的重发行，不产生新的 driver_code，没有任何读法能把它的 100 个司机变成 118 个。AD-Slip-05 的 118 个不同司机多于任何其他站点，且第一名无并列。答案唯一为 AD-Slip-05。
