## Traps
A retired SKU near the top has stock 0; the active minimum is at row 2078 with stock 1.

## Reference solution
awk filter active | sort -k4 -n | head.

## Why the answer is unique
SKU02078 with stock 1; the only active row with stock below 12. Expected answer per turn: SKU02077.
