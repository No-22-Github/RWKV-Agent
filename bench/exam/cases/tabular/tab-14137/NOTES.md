## Traps
- TR-DECOY: 有 3 行 status=cancelled，把它们算进去得到的合计会更大，三个数都会错。
- 输出必须是可解析的 JSON（整段回答或唯一代码块）。

## Reference solution
1. 读 sales/orders.csv（1 步），按 region 汇总 status=paid 的 amount，回答 JSON。

## Why the answer is unique
只有 paid 行计入；cancelled 行包含在内的合计与正确值不同。三个区域合计分别为 North=2533, South=3519, East=2640。

EXAM-CANARY-9f86adfb
