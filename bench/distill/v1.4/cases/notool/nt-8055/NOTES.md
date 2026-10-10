## Traps
- 无。

## Reference solution
1. calculator：8.76 * 1000 / (6.8 * 8760) * 100，precision 1 → 14.7（先把 GWh 换成 MWh）。
终答示例：容量系数约 14.7%（8.76 GWh ÷ (6.8 MW × 8760 h)）。。判据：包含 14.7（千分位 / 去尾零写法均可），调用过 calculator。

## Why the answer is unique
GWh 到 MWh 的换算与全年小时数都是确定的。
