## Traps
- TR-DUPROW: 9 月初网关超时让导出把 26 行扫描在同一 scan_id 下整行重发（RT-Cinder-07 的行段里，重复行与原行逐字节相同）。RT-Cinder-07 以 126 行位居行数第一（其中只有 100 个不同包裹）；按行数排名会交出 RT-Cinder-07。题面问的是不同包裹数：RT-Elder-05 以 118 个不同包裹排在第一，它的行全部集中在导出尾部、超出 read_file 的 64 KB 截断线，必须检索定位后读行段。

## Reference solution
1. read_file README.md：一行一次装车扫描，重写段让个别行整行重复，行数不是包裹数。
2. read_lines 抽样表头附近，确认列格式与路线代码清单。
3. search_text "RT-Cinder-07"（行数最多的候选）：126 次命中，其中 26 次是整行重发，只有 100 个不同包裹。
4. search_text "RT-Elder-05"：118 次命中，全部是不同包裹，行段集中在文件尾部。
5. 其余路线逐一检索同法核对，均不足 118 个不同包裹；胜者为 RT-Elder-05。

## Why the answer is unique
decoy RT-Cinder-07 只在行数上领先，多出的 26 行是逐字节重复的重发行，不产生新的 parcel_id，没有任何读法能把它的 100 个不同包裹变成 118 个。RT-Elder-05 的 118 个不同包裹多于任何其他路线，且第一名无并列。答案唯一为 RT-Elder-05。
