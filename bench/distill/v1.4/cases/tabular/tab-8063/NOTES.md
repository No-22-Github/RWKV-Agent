## Traps
- None.

## Reference solution
1. read_file irrigation/log.csv (30 rows) or data_query with an expression for minutes*l_per_min on zone ZB.
2. calculator: sum of products / 1000, precision 2 = 11.21.
Final answer：Zone ZB used 11.21 m3 (sum of minutes x L/min, divided by 1000).。判据：contains 11.21 (thousands separator / trailing zeros optional), calculator used。

## Why the answer is unique
Each row is a separate run with its own flow rate, so products are summed row by row.
