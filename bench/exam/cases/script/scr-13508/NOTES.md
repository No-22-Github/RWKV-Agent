## Traps
- 沙箱里没有 python：直接运行脚本失败，需要读脚本并用 awk 等方法按同样规则复算。
- TR-DECOY: 不看脚本规则、直接把 gross 全加得 17154.45；规则是排除 cancelled 并减去 refund。
## Reference solution
1. read_file scripts/net_revenue.py（1）
2. 运行 python 失败或判断不可运行（可选）
3. bash awk 按规则复算 = 10617.46（2–3）。ref_calls=3。
## Why the answer is unique
脚本输出 `net revenue: 10617.46`：除 cancelled 外每行 gross-refund 求和。答案由 data/orders.csv 唯一确定。

EXAM-CANARY-4b19d7a0
