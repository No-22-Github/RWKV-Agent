## Traps
- TR-DECOY: matching '.env*' gives 39; the README's rule gives 9.
- 234 files in nested folders under services/, so counting by listing is not practical.

## Reference solution
1. bash: `find services -type f -name .env | wc -l` -> 9
Final answer: 9 files named exactly .env (templates and .envrc excluded).

## Why the answer is unique
The README fixes which names count; matching by that rule over the whole tree gives one number.
