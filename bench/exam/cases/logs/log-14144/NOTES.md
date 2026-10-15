## Traps
- TR-DECOY: counts must be per level; total lines is 40, not any single level.
- Format: reply or its one fenced block must parse as JSON.

## Reference solution
1. read worker.log; 2. count levels {'INFO': 19, 'WARN': 8, 'ERROR': 9, 'DEBUG': 4}; 3. JSON.

## Why the answer is unique
Four distinct counts {'INFO': 19, 'WARN': 8, 'ERROR': 9, 'DEBUG': 4}; all four numbers must appear.

EXAM-CANARY-35b8ad5c
