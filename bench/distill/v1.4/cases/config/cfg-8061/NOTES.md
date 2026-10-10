## Traps
- None.

## Reference solution
1. read_file site/genset.yaml: fuel_burn_lph 14.6, daily_run_hours 9.5.
2. calculator: 14.6 * 9.5 * 30 * 1.38 = 5742.18.
Final answer：Fuel over 30 days costs $5742.18 (14.6 L/h x 9.5 h x 30 x $1.38).。判据：contains 5742.18 (thousands separator / trailing zeros optional), calculator used。

## Why the answer is unique
Both parameters are in the config; price and days are in the prompt.
