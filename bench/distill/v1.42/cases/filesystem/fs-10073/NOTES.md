## Traps
- TR-DECOY: matching 'test_*' (.pyc and .txt counted) gives 29; the README's rule gives 23.
- 183 files in nested folders under src/, so counting by listing is not practical.

## Reference solution
Turn 1: bash: `find src -type f -name '*.py' -not -path '*/tests/*' | wc -l` -> 68
Turn 2: bash: `find src -type f -name 'test_*.py' | wc -l` -> 23
Final answer: 23 test modules.

## Why the answer is unique
The README fixes which names count; matching by that rule over the whole tree gives one number.
