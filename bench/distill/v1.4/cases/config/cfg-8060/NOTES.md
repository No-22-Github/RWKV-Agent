## Traps
- 放数比例只在配置里；不读配置直接乘 18650 × 7.5 会漏掉放数

## Reference solution
1. read_file 印刷/开机参数.yaml：waste_allowance_pct: 3.5。
2. calculator：18650 * 7.5 * 1.035 → 取整 144771。
终答示例：按 3.5% 放数，一共要印 144771 印张（18650 × 7.5 × 1.035）。。判据：包含 144771（千分位 / 去尾零写法均可），调用过 calculator。

## Why the answer is unique
放数比例只在配置里，取整方式由题面指定。
