## Traps
- TR-DECOY: /refund 下面有完全相同的三行超时（第 10–12 行），只能改 /pay 的第 4–6 行。

## Reference solution
1. 读 网关/路由.yaml：/pay 的三行超时在第 4–6 行（连接 2、读 10、写 10）。
2. replace_lines start_line 4、end_line 6，content 三行：「    连接超时秒: 5」「    读超时秒: 5」「    写超时秒: 5」（四格缩进）。
3. 回读确认 /refund 未变。
终答一句话：已把 网关/路由.yaml 中 /pay 的连接、读、写超时（第 4–6 行）都改成 5 秒，/refund 没动。判据：文件逐字节相等；终答提到 /pay。

## Why the answer is unique
三行连续，行号范围必须正好覆盖 4–6；缩进要保持四格，结果唯一。
