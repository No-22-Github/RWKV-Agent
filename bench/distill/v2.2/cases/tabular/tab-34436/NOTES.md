## Traps
The note column has quoted commas, so column positions shift for some rows; the amount is always the last field.

## Reference solution
head -5 to see quoting; awk -F, with $NF.

## Why the answer is unique
Recomputed with python csv. Expected answer per turn: 25236.29.
