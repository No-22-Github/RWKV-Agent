## Traps
CRLF line endings: the last field is failed plus carriage return.

## Reference solution
inspect with cat -A or od; strip CR with tr -d; then awk.

## Why the answer is unique
70 failed, 55 skipped.
Expected: 70; 55
