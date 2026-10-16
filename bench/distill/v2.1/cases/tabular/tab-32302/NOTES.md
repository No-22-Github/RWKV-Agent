## Traps
Region values end with a space, exact match gets 0.

## Reference solution
awk -F, with gsub trim on $3.

## Why the answer is unique
Five customers are 华南.
Expected: 72
