## Traps
- 无。

## Reference solution
1. read_file 灭菌/锅炉参数.yaml：hold_temp_f: 273。
2. calculator：(273 - 32) * 5 / 9，precision 1 → 133.9。
终答示例：保温温度 273 °F，折合约 133.9 °C（(273 − 32) × 5 ÷ 9）。。判据：包含 133.9（千分位 / 去尾零写法均可），调用过 calculator。

## Why the answer is unique
配置里只有 hold_temp_f 一个温度字段需要换算。
