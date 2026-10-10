## Traps
- None.

## Reference solution
1. read_file port/crane.cfg: lift_capacity_lb = 88000.
2. calculator: 88000 * 0.45359237 / 1000 = 39.92.
Final answer：39.92。判据：expected_number 39.92, calculator used。

## Why the answer is unique
Only lift_capacity_lb is a mass in pounds; the spreader weight line is in kg and not used.
