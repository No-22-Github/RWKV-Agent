## Traps
awk strftime is not implemented; use date -d @.

## Reference solution
loop date -d @epoch +%F | grep -c.

## Why the answer is unique
days from the epochs.
Expected: 94; 123
