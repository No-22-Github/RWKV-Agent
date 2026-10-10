## Traps
- 无。

## Reference solution
1. read_file 粮仓/通风.yaml：fan_count 3，flow_m3_per_h 18500。
2. calculator：3 * 18500 * 7.2 / 10000，precision 2 → 39.96。
终答示例：一次开机共送风约 39.96 万立方米（3 台 × 18500 m³/h × 7.2 h ÷ 10000）。。判据：包含 39.96（千分位 / 去尾零写法均可），调用过 calculator。

## Why the answer is unique
台数和单台风量都在配置里，开机时长在题面。
