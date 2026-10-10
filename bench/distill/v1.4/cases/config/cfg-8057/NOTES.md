## Traps
- None.

## Reference solution
1. read_file solar/array.yaml: strings (18, 545), (20, 550), (22, 540).
2. calculator: (18*545 + 20*550 + 22*540) / 1000 = 32.69.
Final answer：The plant's DC capacity is 32.69 kW (sum of panels x watts over the three strings, divided by 1000).。判据：contains 32.69 (thousands separator / trailing zeros optional), calculator used。

## Why the answer is unique
Three strings, all listed; the inverter limit line is not part of the DC sum.
