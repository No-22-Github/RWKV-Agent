## Traps
- TR-DECOY: 单笔最大的配送是 QS-102 的 18 桶（9 月初、位置很靠前），按单笔印象会交出 QS-102；但 QS-102 的月度合计只有 560 桶。题面问月度合计：QS-105 以 890 桶排第一，它的行段集中在导出尾部、超出 read_file 的 64 KB 截断线。

## Reference solution
1. read_file README.md：桶数为本次送达量，排名按员工合计。
2. search_text "QS-102" 定位该员工行段并 read_lines 核对：合计 560 桶，其中单笔最大 18 桶。
3. search_text "QS-105" 定位行段（尾部）并 read_lines：合计 890 桶。
4. 其余员工逐一检索核对，均不足 890 桶。
5. 胜者为 QS-105。

## Why the answer is unique
decoy QS-102 的合计 560 低于 QS-105 的 890，单笔大小不改变月度合计；桶数逐行在列，按员工求和只有一种结果，且第一名无并列。答案唯一为 QS-105。
