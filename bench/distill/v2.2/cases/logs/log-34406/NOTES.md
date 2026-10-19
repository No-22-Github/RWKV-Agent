## Traps
Warn lines also look alarming; the first error is at line 1504.

## Reference solution
grep -n '"lvl":"error"' | head -1.

## Why the answer is unique
Single first error line. Expected answer per turn: 1504; billing/ledger write rejected: duplicate key.
