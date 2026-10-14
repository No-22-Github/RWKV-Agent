## Traps
- No table query tool: a shell pipeline (awk) over the csv is the intended replacement.

## Reference solution
bash: sort -t, -k5 -rn | head -1 -> O20135

## Why the answer is unique
Amounts are distinct at the top, so one id.
