## Traps
Status values are written Refunded; a case-sensitive grep for refunded returns 0.

## Reference solution
head orders.csv; grep -ci refunded orders.csv; awk with tolower for the amount sum.

## Why the answer is unique
Seven rows have Status Refunded; the amount sum follows from them.
Expected: 40; 248
