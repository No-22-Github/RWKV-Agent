## Traps
- None.

## Reference solution
1. data_query: lane=NGB-HAM, avg transit_hours (or sum and count).
2. calculator: mean / 24, precision 2 = 21.33.
Final answer：NGB-HAM shipments average 21.33 days of transit (mean hours / 24).。判据：contains 21.33 (thousands separator / trailing zeros optional), calculator used。

## Why the answer is unique
Mean over the lane's rows, then hours to days.
